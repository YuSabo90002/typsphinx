# Phase 42 Plan 03 — Gate Evidence: Repo-Wide Anchor-Misrouting Sweep (D-06/D-07)

**Measured at commit:** `19a6378e6b12ec086e3e3af11f93e736a30c0cb3`
(`git log -1 --oneline` → `19a6378 docs(42): record planning completion in state`)

**Tree state at this commit: UNFIXED.** `depart_table`'s call ordering has NOT yet been changed
by plan 42-04 — the `_emit_id_anchors` call at `typsphinx/translator.py:3341` still fires while
`self.in_table` is still `True` (cleared two lines later, at `:3351`). This plan runs in wave 1
against this tree deliberately, so the sweep below observes the misrouting class live, not as
history. All line numbers in this file are as observed at this commit and will shift once 42-04
lands — they are recorded as observed, not "helpfully" pre-adjusted.

This file is derived entirely from reading the live tree in THIS worktree. No table or row below
is transcribed from `42-RESEARCH.md` § 5, which D-07 rules inadmissible as phase evidence.

---

## 1. Static half of the sweep (Task 1)

### 1.1 `add_text` — the single source of truth for which flags divert an append

Command: `sed -n '423,437p' typsphinx/translator.py`

```python
    def add_text(self, text: str) -> None:
        """
        Add text to the output body or table cell content.

        Args:
            text: The text to add
        """
        if (
            hasattr(self, "in_table")
            and self.in_table
            and hasattr(self, "table_cell_content")
        ):
            self.table_cell_content.append(text)
        else:
            self.body.append(text)
```

`add_text` branches on exactly one condition: `self.in_table` truthy AND
`hasattr(self, "table_cell_content")`. **`self.in_table` is the only flag `add_text` consults.**
No other `self.in_*` attribute (`in_figure`, `in_caption`, `in_list_item`,
`in_captioned_code_block`, `in_paragraph`, `in_literal_block`, `in_signature_text`,
`in_definition_list`, `in_thead`, `in_desc_parameter`) appears anywhere in `add_text`'s body. This
means: **the ONLY way a call to `self.add_text(...)` can be silently diverted away from
`self.body` is if `self.in_table` is `True` at that moment** — every other flag governs some other
piece of bookkeeping (separator logic, wrapper selection) but has zero effect on where `add_text`
writes.

### 1.2 Enumeration of every `_emit_id_anchors(` call site

Command: `grep -n '_emit_id_anchors(' typsphinx/translator.py`

```
481:    def _emit_id_anchors(
853:        self._emit_id_anchors(node)
884:            self._emit_id_anchors(node)
960:        self._emit_id_anchors(node)
1777:        self._emit_id_anchors(node)
1832:        self._emit_id_anchors(node)
1910:        self._emit_id_anchors(node)
1961:        self._emit_id_anchors(node)
2133:        self._emit_id_anchors(node)
2518:        self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))
3175:            self._emit_id_anchors(node)
3341:                self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))
3532:        self._emit_id_anchors(node)
3644:            self._emit_id_anchors(node)
4814:        self._emit_id_anchors(node)
4902:        self._emit_id_anchors(node)
5137:            self._emit_id_anchors(node)
5169:            self._emit_id_anchors(node)
5310:        self._emit_id_anchors(node)
5336:        self._emit_id_anchors(node)
5447:        self._emit_id_anchors(node)
6392:        self._emit_id_anchors(node)
```

21 call sites (excluding the method's own `def` at line 481), each enumerated and classified
below.

### 1.3 Enumeration of every `self.in_<name> = True` / `= False` assignment

Command: `grep -n 'self\.in_[a-zA-Z_]* = True\|self\.in_[a-zA-Z_]* = False' typsphinx/translator.py`

```
161:        self.in_figure = False
162:        self.in_table = False
167:        self.in_thead = False  # Track if currently in table header
168:        self.in_caption = False
205:        self.in_captioned_code_block = False
210:        self.in_paragraph = False
212:        self.in_list_item = False  # Track if currently in a list item
220:        self.in_literal_block = False  # Track if currently in a code block
231:        self.in_signature_text = False
313:        self.in_definition_list = False
670:            self.in_list_item = True
683:        self.in_list_item = True
814:        self.in_paragraph = False
887:            self.in_captioned_code_block = True
909:            self.in_captioned_code_block = False
971:            self.in_paragraph = False
980:            self.in_paragraph = False
984:        self.in_paragraph = True
1013:            self.in_paragraph = False
1026:        self.in_paragraph = False
1429:        self.in_paragraph = False
1437:        self.in_list_item = True
1539:        self.in_paragraph = False
1547:        self.in_list_item = True
1701:        self.in_paragraph = False
1741:        self.in_paragraph = False
1889:        self.in_list_item = True
1932:            self.in_list_item = False
1968:        self.in_literal_block = True
2089:        self.in_literal_block = False
2147:        self.in_definition_list = True
2170:            self.in_definition_list = True
2173:            self.in_definition_list = False
2439:        self.in_figure = True
2522:        self.in_figure = False
2565:            self.in_paragraph = True
2568:        self.in_caption = True
2589:        self.in_caption = False
2700:            self.in_paragraph = False
3035:        self.in_paragraph = False
3194:        self.in_table = True
3351:        self.in_table = False
3423:        self.in_thead = True
3433:        self.in_thead = False
5175:            self.in_paragraph = True
5626:        self.in_paragraph = False
5634:        self.in_list_item = True
5644:        self.in_signature_text = True
5718:        self.in_signature_text = False
6020:        self.in_desc_parameter = True
6031:        self.in_desc_parameter = False
6209:        self.in_paragraph = False
6430:        self.in_paragraph = False
6438:        self.in_list_item = True
```

Cross-referencing this list against §1.1: only two of these assignments — `self.in_table = True`
(`:3194`, `visit_table`) and `self.in_table = False` (`:3351`, `depart_table`) — toggle the one
flag `add_text` actually branches on. Every other assignment in this list toggles a flag that has
no effect on where `add_text` routes.

### 1.4 The two false-positive classes this sweep must NOT count as findings

**Class A — a call site nested inside a table cell, routing into `table_cell_content`, is
DESIRED behavior and not a finding.** `self.in_table` stays `True` for the entire span between
`visit_table` (`:3194`) and `depart_table` (`:3351`), and docutils' table model allows a cell to
contain arbitrary body elements — paragraphs, lists, literal blocks, definition lists, block
quotes, admonitions, and so on. When any of THOSE elements' own `visit_*` handler calls
`_emit_id_anchors` while nested inside a cell, `self.in_table` is `True` because an ENCLOSING
table opened it, not because the element itself did — and routing that anchor into
`table_cell_content` is exactly where a cell's own content is supposed to go (it is assembled into
the cell string by `visit_entry`/`depart_entry`, not discarded). The defect this sweep targets is
narrower and different: **a node emitting its OWN trailing anchor while the buffer diversion IT
itself opened for its children is still active** — i.e. the anchor is not content belonging inside
that diversion, it is metadata about the node that owns the diversion, and it gets swept into a
buffer that node itself is about to discard. `depart_table` (§1.5 below) is exactly this shape;
a `visit_paragraph` firing inside a table cell is not.

**Class B — a body-swap idiom that temporarily replaces `self.body` is not the same hazard.**
Three such idioms exist in this file, and all three are fully contained within one child node's
`visit_*`/`depart_*` pair, restored before the enclosing node's own depart-time anchor call could
ever fire:

- **Admonition-title swap** (`visit_title`/`depart_title`, `:704-706` open / `:762-769` restore):
  `self._saved_body_for_admonition_title = self.body; self.body = []` on `visit_title` entry,
  restored via `self.body = self._saved_body_for_admonition_title` on `depart_title` exit — the
  swap lives entirely inside the `title` child's own visit/depart pair. The enclosing
  admonition's own `_emit_id_anchors` call (`:4902`, inside `_visit_admonition`) runs on the
  admonition's OWN `visit_*`, before any title child is even visited, so it can never observe the
  swapped buffer.
- **Figure-caption swap** (`visit_caption`/`depart_caption`, `:2550-2552` open / `:2581-2585`
  restore): `self._saved_body_for_figure_caption = self.body; self.body = []` on `visit_caption`
  entry (guarded by `self.in_figure`), restored via
  `self.body = self._saved_body_for_figure_caption` on `depart_caption` exit — again fully
  contained within the `caption` child's own pair, always closed before `depart_figure`
  (`:2518`'s `_emit_id_anchors` call site) runs.
  - **The `_in_table_caption` consumer is the D-08-relevant analogue of this same idiom for
    tables** — `depart_title` (`:753-760`) checks `self._in_table_caption` FIRST (before the
    admonition-title branch) and, when true, joins `self.table_cell_content` into
    `self.table_caption` and clears `self.table_cell_content`. This assigns
    `self.table_caption` from the STRIPPED, joined buffer — the truthiness axis `depart_table`'s
    captioned-vs-caption-less branch (`:3304`) tests. This consumer is read-only with respect to
    the anchor-misrouting question this sweep answers (it does not call `_emit_id_anchors`), but
    it is the exact code the D-08 todo (Task 3, below) is filed against.
- **Definition-list term/definition buffers** (`visit_term`/`depart_term`,
  `:2318-2320` open / `:2356` restore; `visit_definition`/`depart_definition`, `:2380-2387` open /
  `:2407` restore): both push `self.body` onto `self._saved_body_stack` and pop it back on their
  own depart, before the enclosing `definition_list_item`'s own processing continues.
  `visit_definition_list` (`:2133`) — the only `_emit_id_anchors` call site in this family — fires
  on the LIST's own visit, before any `term`/`definition` child is visited, so it can never
  observe either swapped buffer either.

None of these three idioms is the hazard class 1.1 identifies: each swap is opened and closed
within a single child's own visit/depart pair, strictly BEFORE the enclosing node's own anchor
call (if any) can fire — unlike `self.in_table`, which stays open across `visit_table` ...
`depart_table`'s ENTIRE span, including `depart_table`'s own trailing anchor call.

### 1.5 Classification table — one row per `_emit_id_anchors(` call site

| Line | Owning method | Own anchor vs. nested content | Diverting flag set at call moment | Verdict | Image-path? |
|---|---|---|---|---|---|
| 853 | `visit_compound` | Own (compound's own ids) | None (visit-side, before any flag this node itself sets) | SAFE | non-image |
| 884 | `visit_container` | Own (container's own ids, `names`-guarded) | None (visit-side) | SAFE | non-image |
| 960 | `visit_paragraph` | Own OR nested-in-cell (Class A when `in_table` is True from an enclosing table) | None self-set; `in_table` may be True from an ENCLOSING table — Class A, desired | SAFE | non-image |
| 1777 | `visit_bullet_list` | Own / nested-in-cell (Class A) | None self-set | SAFE | non-image |
| 1832 | `visit_enumerated_list` | Own / nested-in-cell (Class A) | None self-set | SAFE | non-image |
| 1910 | `visit_list_item` | Own | `in_list_item` (set True at `:1889`, just above) — NOT consulted by `add_text` (§1.1) | SAFE | non-image |
| 1961 | `visit_literal_block` | Own / nested-in-cell (Class A) | None self-set at call moment (`in_literal_block` set True after, at `:1968`) | SAFE | non-image |
| 2133 | `visit_definition_list` | Own / nested-in-cell (Class A) | None self-set (`in_definition_list` set True after, at `:2147`) | SAFE | non-image |
| 2518 | `depart_figure` | Own (figure's propagated-remainder ids, `skip_ids={ids[0]}`) | `in_figure` is still True (cleared after, at `:2522`) — but `in_figure` is NOT consulted by `add_text` (§1.1) | SAFE | **IMAGE-PATH** |
| 3175 | `visit_table` (non-captioned branch only) | Own | None — fires BEFORE `self.in_table = True` (`:3194`, 19 lines later) | SAFE | non-image |
| 3341 | `depart_table` (captioned branch) | Own (table's propagated-remainder ids, `skip_ids={ids[0]}`) | `self.in_table` is STILL True — cleared 10 lines later, at `:3351` | **MISROUTED** | non-image |
| 3532 | `visit_block_quote` | Own / nested-in-cell (Class A) | None self-set | SAFE | non-image |
| 3644 | `visit_image` | Own (guarded `not self.in_figure`) | None self-set; `in_table` False for a standalone image | SAFE | **IMAGE-PATH** |
| 4814 | `visit_math_block` | Own | None self-set | SAFE | non-image |
| 4902 | `_visit_admonition` | Own | None self-set | SAFE | non-image |
| 5137 | `visit_topic` (`.. contents::` branch) | Own | None self-set | SAFE | non-image |
| 5169 | `visit_line_block` (depth 0 only) | Own | None self-set | SAFE | non-image |
| 5310 | `visit_transition` | Own / nested-in-cell (Class A) | None self-set | SAFE | non-image |
| 5336 | `visit_glossary` | Own | None self-set | SAFE | non-image |
| 5447 | `visit_desc` | Own | None self-set | SAFE | non-image |
| 6392 | `visit_rubric` | Own | None self-set | SAFE | non-image |

**`depart_table` (:3341) is verdict MISROUTED.** **`visit_table` (:3175) is verdict SAFE**, with
the reason recorded in the table: it fires before `self.in_table = True` is ever assigned
(`:3194`), so `add_text`'s single diverting condition (§1.1) cannot be true at that call.

### 1.6 A secondary observation, NOT a MISROUTED finding

`visit_rubric` (`:6392`) measures `anchors_were_emitted` via `len(self.body)` before/after its
`_emit_id_anchors` call, to decide whether to suppress a redundant separator (D-11). If a rubric
were ever nested inside a table cell (`self.in_table` True from an enclosing table — Class A), the
anchor would correctly land in `table_cell_content`, but `len(self.body)` would not grow, so
`anchors_were_emitted` would read `False` even though an anchor WAS emitted. This is a
**separator/spacing bookkeeping bug**, not an anchor-drop: the id still lands in the correct
buffer and the reference still resolves. It does not match this sweep's defect predicate (a
node's own anchor call landing in a buffer that gets DISCARDED), so it is not filed as a finding
here. Recorded for completeness only, not acted on.

### 1.7 Finding list (static half)

**The only MISROUTED row is `depart_table` (:3341).** This is exactly this phase's own
already-known defect (TBL-03), whose fix is 42-04's job (call-ordering move per D-05) — it is not
a NEW finding this sweep surfaces, it is the sweep confirming no OTHER call site shares the same
shape. No other call site in §1.5 is MISROUTED. Consequently there is no non-image finding to file
a todo for from this task; the sweep's non-image output is a clean bill for every call site other
than the phase's own known defect.

## 2. Image-path re-measurement, formal, with a real build (Task 2, D-07)

D-07's requirement: the image-path measurement made during phase discussion
(`42-CONTEXT.md` § "Measured during this discussion (scratchpad only — NOT phase evidence)") is
reference material only and is NOT admissible as phase evidence. This section re-takes that
measurement from scratch, formally, inside this plan, against a real `-b typstpdf` build. §1.5
above flagged two IMAGE-PATH call sites — `depart_figure` (`:2518`) and `visit_image` (`:3644`) —
each already classified SAFE by static reading (neither observes `self.in_table`, the only flag
`add_text` branches on). This section verifies that classification with an executable measurement,
per the owner's condition (D-06): "an image-path finding is fixed inside this phase."

### 2.1 Probe project

Built under the session scratchpad, **not** under `tests/`, `typsphinx/`, `docs/`, or `examples/`,
and not committed to the repository. Two shapes, matching the two IMAGE-PATH call sites: a
standalone target immediately before a bare `.. image::`, and a standalone target immediately
before a captioned `.. figure::`, each followed by a `:ref:` back to the target with explicit link
text. The image file is a 1×1 PNG copied from the already-committed
`tests/fixtures/figure_target_caption_render_gate/image.png` fixture asset — no new binary
introduced.

`conf.py` (verbatim):

```python
"""THROWAWAY probe project -- Phase 42 Plan 03, D-07 formal image-path re-measurement.

Not committed to the repository. Built under the session scratchpad only, to
formally re-take (per D-07) the image-path measurement that 42-CONTEXT.md's
"Measured during this discussion (scratchpad only -- NOT phase evidence)"
section reports informally: whether a standalone target immediately preceding
a bare `.. image::` or a captioned `.. figure::` drops its propagated id the
same way depart_table does.
"""

project = "Image Path Probe"
author = "typsphinx tests"
release = "0.0.0"

extensions = ["typsphinx"]

# index must be a master document so the writer emits the full template.
typst_documents = [
    ("index", "index", "Image Path Probe", "typsphinx tests"),
]
```

`index.rst` (verbatim):

```rst
Image Path Probe
=================

Bare Image Shape
-----------------

.. _img-target:

.. image:: image.png

See the :ref:`bare image target <img-target>`.

Captioned Figure Shape
------------------------

.. _fig-target:

.. figure:: image.png

   A caption.

See the :ref:`captioned figure target <fig-target>`.
```

### 2.2 Build command, exit status, stderr

Command (run from inside this worktree, per the standing `uv run` provisioning requirement):

```
uv run python -m sphinx -b typstpdf -q -E "$PROBE_DIR" "$OUT_DIR"
```

Exit status: **`0`**

stdout: empty (the `-q` flag suppresses normal build-progress lines; none printed because there
were none to suppress beyond the standard progress banner, which `-q` elides).

stderr: **empty** — no warnings, no errors, no `TypstCompilationError`.

Output directory listing after the build:

```
_template.typ
image.png
index.pdf     (23854 bytes)
index.typ
.doctrees/
```

`index.pdf` **was produced** — a real, non-empty PDF, not a partial/failed artifact.

### 2.3 Emitted `.typ` — label definitions and link references

Full emitted `index.typ` body (verbatim):

```typst
#{
[#heading(level: 1, {text("Image Path Probe")}) <index:image-path-probe>]

[#heading(level: 2, {text("Bare Image Shape")}) <index:bare-image-shape>]


[#metadata(none) <index:img-target>]
image("image.png")

par({text("See the ")
link(<index:img-target>, 
text("bare image target"))
text(".")})


[#heading(level: 2, {text("Captioned Figure Shape")}) <index:captioned-figure-shape>]

[#figure(
  image("image.png"),
  caption: {text("A caption.")}
) <index:id1>]


[#metadata(none) <index:fig-target>]
par({text("See the ")
link(<index:fig-target>, 
text("captioned figure target"))
text(".")})



}
```

Command: `grep -n '<index:' index.typ`

```
20:[#heading(level: 1, {text("Image Path Probe")}) <index:image-path-probe>]
22:[#heading(level: 2, {text("Bare Image Shape")}) <index:bare-image-shape>]
25:[#metadata(none) <index:img-target>]
29:link(<index:img-target>, 
34:[#heading(level: 2, {text("Captioned Figure Shape")}) <index:captioned-figure-shape>]
39:) <index:id1>]
42:[#metadata(none) <index:fig-target>]
44:link(<index:fig-target>,
```

Command: `grep -n 'link(' index.typ`

```
29:link(<index:img-target>, 
44:link(<index:fig-target>,
```

### 2.4 Per-call-site verdict

- **Bare `.. image::` site (`visit_image`, `:3644`).** The standalone target `.. _img-target:`
  propagates onto the `image` node's `ids`. Line 25 shows `[#metadata(none) <index:img-target>]`
  emitted by `visit_image`'s `_emit_id_anchors(node)` call, immediately before the `image(...)`
  call on line 26. Line 29's `link(<index:img-target>, ...)` — the compiled `:ref:` — resolves
  against it. **No misrouting. SAFE, confirmed by real build.**
- **Captioned `.. figure::` site (`depart_figure`, `:2518`).** The figure has no `:name:`, so
  docutils assigns the auto id `id1` to `ids[0]` (self-anchored as the figure's own `<label>` at
  line 39, per D-02 — the first id always owns the figure label). The standalone target
  `.. _fig-target:` propagates a SECOND id onto `ids[1:]`, anchored separately by
  `depart_figure`'s `_emit_id_anchors(node, skip_ids={ids[0]})` call at line 42. Line 44's
  `link(<index:fig-target>, ...)` resolves against it. **No misrouting. SAFE, confirmed by real
  build.**

### 2.5 NULL RESULT — D-06's image-path condition is moot

**No image-path misrouting exists.** Both IMAGE-PATH call sites flagged in §1.5 (`visit_image`
and `depart_figure`) were re-measured here with a real `-b typstpdf` build, independently of the
static classification in §1 and independently of the discussion-time measurement D-07 rules
inadmissible. The commands that established this: the `sphinx -m sphinx -b typstpdf -q -E`
invocation in §2.2 (exit `0`, empty stderr, `index.pdf` produced), and the `grep -n '<index:'` /
`grep -n 'link('` commands in §2.3, whose output shows every `link(<index:...>)` reference matched
by a `<index:...>` label definition — including the propagated-target labels `img-target` and
`fig-target`, the exact class of id `depart_table`'s bug drops. Measured at commit
`19a6378e6b12ec086e3e3af11f93e736a30c0cb3` (same commit as §1, unfixed tree). **D-06's condition
"an image-path finding is fixed inside this phase" is therefore moot — there is nothing to fix.**
No production code was changed by this plan.

**Cross-reference, not a dependency:** the figure half of the image path is ALSO permanently
gated by plan 42-02's `tests/test_figure_propagated_target_render_gate.py` (a parallel wave-1
plan, not present in this worktree). That gate and this measurement are independent lines of
evidence for the same conclusion — this section does not depend on it, and was measured
standalone.

## 3. Summary — D-06 and D-07 disposition

- **D-06 (repo-wide sweep, result recorded either way):** satisfied. §1 is the static half (21
  call sites enumerated and classified from the live tree); §2 is the dynamic image-path half (a
  real build). The sole MISROUTED finding across both halves is `depart_table` — the phase's own
  already-known defect, fixed by plan 42-04, not a new finding requiring its own todo. The
  image-path half is a NULL RESULT (§2.5) — D-06's "fixed inside this phase" branch does not
  fire.
- **D-07 (image-path measurement re-taken formally, discussion-time measurement inadmissible):**
  satisfied. §2 is a from-scratch, real-build measurement taken inside this plan's own worktree at
  a named commit, independent of `42-CONTEXT.md`'s discussion-time scratchpad measurement and of
  `42-RESEARCH.md` § 5.


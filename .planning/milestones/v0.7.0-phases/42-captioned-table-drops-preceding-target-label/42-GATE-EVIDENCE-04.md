# Phase 42, Plan 04 — GATE-04 Evidence (TBL-03, GREEN + regression sweep)

Discharges ROADMAP SC#3 (captioned table preceded by a standalone target compiles, both labels
resolve, no duplicate-label fatal) and SC#5's GREEN half (the fix landed in a separate, later
commit than the recorded RED, proven by ancestry). Every number below was transcribed from a
command actually run in THIS worktree.

---

## 1. Commit ordering (SC#5)

**RED-recording commit** (quoted from `42-GATE-EVIDENCE-01.md` § 1):

```
d28f2c8bcdf8aee49ab82b1d883145a4036acefc
```

```
d28f2c8 test(42-01): record classic RED for captioned-table propagated-target drop
```

**This plan's fix commit:**

**Command:** `git rev-parse HEAD`

```
e5575f3ab51144405c44764a5b192b9d5f7526b2
```

**Command:** `git log -1 --oneline HEAD`

```
e5575f3 fix(42-04): move captioned-table propagated-anchor call past in-table reset
```

**Ancestry check.**

**Command:** `git merge-base --is-ancestor d28f2c8bcdf8aee49ab82b1d883145a4036acefc e5575f3ab51144405c44764a5b192b9d5f7526b2`

```
(exit 0)
```

`git merge-base --is-ancestor` exits `0` (success) when the first commit IS an ancestor of the
second. The exit status here is `0` — `d28f2c8` (RED) is a proper ancestor of `e5575f3` (fix). The
RED was recorded against unfixed source in its own earlier commit
(`42-GATE-EVIDENCE-01.md` § 1 confirms `git status --porcelain typsphinx/` was empty at that
commit — `typsphinx/` was byte-unmodified when the RED was recorded), and the fix landed
separately and later in this plan's own commit. This is the classic GATE-01 ordering that
milestone invariant #4 names TBL-03 as an exception for (RED is a real `TypstError`, not a
structural/regex assertion, because the defect is a compile fatal, not a design-quality defect).

---

## 2. The change (D-05, D-02)

**Command:** `git diff --stat -- typsphinx/` (for the fix commit, `e5575f3`)

```
typsphinx/translator.py | 34 +++++++++++++++++++++++++++-------
1 file changed, 27 insertions(+), 7 deletions(-)
```

`typsphinx/translator.py` is the ONLY production file touched.

**Command:** `git show e5575f3ab51144405c44764a5b192b9d5f7526b2 -- typsphinx/translator.py`

```diff
diff --git a/typsphinx/translator.py b/typsphinx/translator.py
index 136eb97..5c1e2ff 100644
--- a/typsphinx/translator.py
+++ b/typsphinx/translator.py
@@ -3332,13 +3332,6 @@ class TypstTranslator(SphinxTranslator):
                     )
                 else:
                     self.body.append(f"{figure_code}\n\n")
-
-                # TBL-02/Critical Pitfall 3: ids[0] is already self-anchored
-                # above as the figure's own <label> -- anchoring it again
-                # here would define it TWICE (Typst "label ... occurs
-                # multiple times" compile fatal). Anchor only a PROPAGATED
-                # remainder id (ids[1:]); no-op when there is none.
-                self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))
             else:
                 # Caption-less path: byte-for-byte unchanged (SC#2).
                 if converted_width is not None:
@@ -3348,7 +3341,34 @@ class TypstTranslator(SphinxTranslator):
                 else:
                     self.body.append(f"{table_code}\n\n")
 
+        # TBL-03 (Phase 42): captured BEFORE self.table_caption is reset
+        # below, because the original `if self.table_caption:` condition
+        # cannot be re-evaluated after that reset -- re-reading it there
+        # would evaluate False for every captioned table and silently
+        # disable the propagated-anchor emission below while leaving the
+        # caption-less path (which never had a bug) looking correct. The
+        # `self.table_colcount > 0` conjunct mirrors the enclosing guard
+        # this call site sat inside before the move, so a degenerate
+        # zero-column captioned table keeps its current (no-op) emission.
+        was_captioned = self.table_colcount > 0 and bool(self.table_caption)
+
         self.in_table = False
+
+        # TBL-02/Critical Pitfall 3: ids[0] is already self-anchored above
+        # as the figure's own <label> -- anchoring it again here would
+        # define it TWICE (Typst "label ... occurs multiple times" compile
+        # fatal). Anchor only a PROPAGATED remainder id (ids[1:]); no-op
+        # when there is none.
+        #
+        # TBL-03 (Phase 42): this call must run AFTER self.in_table is
+        # cleared above. add_text() (see that method) diverts every append
+        # into self.table_cell_content while self.in_table is set, and that
+        # buffer is `del`eted a few statements below -- so an anchor emitted
+        # from the old pre-reset call site never reached self.body at all;
+        # it was silently discarded along with the buffer.
+        if was_captioned:
+            self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))
+
         self.table_cells = []
         self.table_colcount = 0
         self.table_colwidths = []
```

**What was NOT touched.** `git diff` for this commit shows the entire change confined to
`TypstTranslator.depart_table` (lines ~3332–3375). Specifically, byte-identical (no diff hunk
touches these regions):

- `_emit_id_anchors`'s definition (lines 481–552) — same two parameters (`node`, `skip_ids`), same
  body, no new argument. The owner explicitly declined to widen this shared helper.
- `add_text` (lines 423–437) — the single-flag branch that makes the call-ordering matter is
  unchanged.
- `visit_table`'s unconditional non-captioned call (`self._emit_id_anchors(node)` at line 3175,
  pre-fix numbering) — unchanged.
- `depart_figure` (lines 2480–2531) — unchanged; its own ordering was already correct because
  `add_text` never consults `self.in_figure`.
- The caption-less `else:` branch of `depart_table` — byte-for-byte unchanged, confirmed by the
  diff hunk above showing no line inside that branch (`# Caption-less path: byte-for-byte
  unchanged (SC#2).` through `self.body.append(f"{table_code}\n\n")`) was added, removed, or
  reordered.

`skip_ids=set(node.get("ids", [])[:1])` — the exact argument expression from the pre-fix call
site — was carried across unchanged in the moved call (see the diff's `+` line
`self._emit_id_anchors(node, skip_ids=set(node.get("ids", [])[:1]))`). D-02 is therefore
satisfied: `ids[0]` still owns the figure's own `<label>` (self-anchored earlier in the same
method, in the `figure_code`/`) <{label}>]` block, itself unchanged by this diff), and `ids[1:]`
still become `metadata(none)` anchors via the moved call.

---

## 3. The GREEN (SC#3)

**Command:** `uv run pytest tests/test_captioned_table_propagated_target_render_gate.py -v`

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a2591048a1b399f97
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 9 items

tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_compile_clean PASSED [ 11%]
tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_shape_a_named_target_anchor PASSED [ 22%]
tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_shape_b_noname_target_anchor PASSED [ 33%]
tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_shape_c_list_item_target_anchor PASSED [ 44%]
tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_shape_d_two_consecutive_targets_anchor PASSED [ 55%]
tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_no_duplicate_label_definition PASSED [ 66%]
tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_no_dangling_same_document_reference PASSED [ 77%]
tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_caption_less_control_table_not_figure_wrapped PASSED [ 88%]
tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_pdf_magic_bytes PASSED [100%]

============================== 9 passed in 0.37s ===============================
```

All nine methods pass — including the two that already passed pre-fix
(`test_no_duplicate_label_definition`, `test_caption_less_control_table_not_figure_wrapped`).

### 3.1 A real `-b typstpdf` build, independent of the test module (D-03's structural half)

A bare pass count does not by itself prove BOTH label forms are present with no duplicate
definition — the following is a from-scratch build of the fixture in this worktree, at the fix
commit, whose emitted `.typ` is inspected directly.

**Command:**

```
uv run python -m sphinx -b typstpdf -q -E tests/fixtures/captioned_table_propagated_target_render_gate <build>
```

**Exit status:** `0`

**stdout:** empty (captured to a file; `wc -l` reports `0`)

**stderr:** empty (captured to a separate file; `wc -l` reports `0`) — no
`TypstError`, no `does not exist in the document`, no compilation failure of any kind.

**Output directory listing:**

```
_template.typ
index.pdf     (56231 bytes)
index.typ
.doctrees/
```

`index.pdf` was produced — a real, non-empty PDF (56231 bytes), not a partial/failed artifact.

**Emitted `index.typ` body (verbatim, the four D-01 shapes plus the caption-less control):**

```typst
[#heading(level: 2, {text("Target plus a named captioned table")}) <index:target-plus-a-named-captioned-table>]

[#figure(
table(
  columns: (8fr, 8fr),
  table.header(
    {par({text("Column A")})},
    {par({text("Column B")})},
  ),
  {par({text("Cell")})},
  {par({text("Cell")})},
),
  caption: {text("TBLTGTNAMEDSENTINEL")},
  kind: table
) <index:tbl-name>]


[#metadata(none) <index:tbl-target>]

[#heading(level: 2, {text("Target plus a captioned table with no name")}) <index:target-plus-a-captioned-table-with-no-name>]

[#figure(
table(
  columns: (8fr, 8fr),
  table.header(
    {par({text("Column A")})},
    {par({text("Column B")})},
  ),
  {par({text("Cell")})},
  {par({text("Cell")})},
),
  caption: {text("TBLTGTNONAMESENTINEL")},
  kind: table
) <index:id1>]


[#metadata(none) <index:tbl-target-noname>]

[#heading(level: 2, {text("Target plus a captioned table inside a list item")}) <index:target-plus-a-captioned-table-inside-a-list-item>]

list({
parbreak()

text("Lead-in text before the nested table:")

[#figure(
table(
  columns: (8fr, 8fr),
  table.header(
    {parbreak()

text("Column A")},
    {parbreak()

text("Column B")},
  ),
  {parbreak()

text("Cell")},
  {parbreak()

text("Cell")},
),
  caption: {text("TBLTGTLISTSENTINEL")},
  kind: table
) <index:tbl-name-li>]



[#metadata(none) <index:tbl-target-li>]

})


[#heading(level: 2, {text("Two consecutive targets before one captioned table")}) <index:two-consecutive-targets-before-one-captioned-table>]

[#figure(
table(
  columns: (8fr, 8fr),
  table.header(
    {par({text("Column A")})},
    {par({text("Column B")})},
  ),
  {par({text("Cell")})},
  {par({text("Cell")})},
),
  caption: {text("TBLTGTTWOSENTINEL")},
  kind: table
) <index:tbl-name-two>]


[#metadata(none) <index:tbl-target-b>]

[#metadata(none) <index:tbl-target-a>]

[#heading(level: 2, {text("Caption-less control table")}) <index:caption-less-control-table>]

par({text("A table with no caption, no name, and no preceding target must stay byte-unchanged by this fix – it is not figure-wrapped at all.")})

table(
  columns: (8fr, 8fr),
  table.header(
    {par({text("Column A")})},
    {par({text("Column B")})},
  ),
  {par({text("Cell")})},
  {par({text("Cell")})},
)


[#heading(level: 2, {text("References back to the propagated targets")}) <index:references-back-to-the-propagated-targets>]

par({text("See ")
link(<index:tbl-name>,
text("Table 1"))
text(" for the named table's own cross-reference.")})

par({text("Every reference below is given explicit link text rather than a bare reference, because a bare reference to a captioned table defaults its link text to that table's own caption.")})

list({
parbreak()

link(<index:tbl-target>, text("first target link text"))
}, {
parbreak()

link(<index:tbl-target-noname>, text("second target link text"))
}, {
parbreak()

link(<index:tbl-target-li>, text("third target link text"))
}, {
parbreak()

link(<index:tbl-target-a>, text("fourth target link text"))
}, {
parbreak()

link(<index:tbl-target-b>, text("fifth target link text"))
}, {
parbreak()

link(<index:tbl-name-li>, text("sixth target link text"))
}, {
parbreak()

link(<index:tbl-name-two>, text("seventh target link text"))
})
```

**BOTH label forms present for every D-01 shape** — the `:name:`-derived id owning the figure
`<label>` postfix (e.g. `) <index:tbl-name>]`), and the target-derived id emitted as a
`[#metadata(none) <index:...>]` anchor (e.g. `[#metadata(none) <index:tbl-target>]`):

| Shape | Figure `<label>` (owns `ids[0]`) | Propagated anchor(s) (`ids[1:]`, `metadata(none)`) |
|-------|-----------------------------------|-------------------------------------------------------|
| A — target + `:name:` table | `<index:tbl-name>` | `<index:tbl-target>` |
| B — target + no-`:name:` table | `<index:id1>` (docutils auto id) | `<index:tbl-target-noname>` |
| C — target + table in list item | `<index:tbl-name-li>` | `<index:tbl-target-li>` |
| D — two targets + table | `<index:tbl-name-two>` | `<index:tbl-target-b>`, `<index:tbl-target-a>` |
| Control — caption-less table | (no figure wrap — no `<label>`) | (no propagated target authored — no anchor) |

**No `index:`-namespaced label is defined twice.**

**Command:** `grep -oP '<index:[a-z0-9-]+>\]' index.typ | sort | uniq -c | sort -rn`

```
      1 <index:two-consecutive-targets-before-one-captioned-table>]
      1 <index:tbl-target>]
      1 <index:tbl-target-noname>]
      1 <index:tbl-target-li>]
      1 <index:tbl-target-b>]
      1 <index:tbl-target-a>]
      1 <index:tbl-name>]
      1 <index:tbl-name-two>]
      1 <index:tbl-name-li>]
      1 <index:target-plus-a-named-captioned-table>]
      1 <index:target-plus-a-captioned-table-with-no-name>]
      1 <index:target-plus-a-captioned-table-inside-a-list-item>]
      1 <index:references-back-to-the-propagated-targets>]
      1 <index:id1>]
      1 <index:captioned-table-propagated-target-render-gate>]
      1 <index:caption-less-control-table>]
```

Every label definition count is `1` — none is `2` or higher. The test method that enforces this
generically (over ANY same-document reference, not just this fixture's hand-picked set) is
`test_no_duplicate_label_definition` in
`tests/test_captioned_table_propagated_target_render_gate.py`, which passed above (§ 3).

**Command:** `grep -c 'kind: table' index.typ` → `4`. The caption-less control table is confirmed
NOT figure-wrapped (4 `kind: table` occurrences, one per captioned shape, none for the control),
matching the pre-existing `test_caption_less_control_table_not_figure_wrapped` assertion.

---

## 4. RED-to-GREEN verdict table

| Shape | Pre-fix result (`42-GATE-EVIDENCE-01.md`) | Post-fix result | Verdict |
|-------|---------------------------------------------|--------------------------------------------|---------|
| A — target + `:name:`-carrying table | `label \`<index:tbl-target>\` does not exist in the document` — compile fatal (§2, §4) | Compiles; `<index:tbl-target>` anchor present and resolved by `link(<index:tbl-target>, ...)` (§3.1) | **RED → GREEN** |
| B — target + table with no `:name:` | `<index:tbl-target-noname>` reported dangling (`test_no_dangling_same_document_reference`, §4) | Compiles; `<index:tbl-target-noname>` anchor present and resolved (§3.1) | **RED → GREEN** |
| C — target + table inside a list item | `<index:tbl-target-li>` reported dangling (§4) | Compiles; `<index:tbl-target-li>` anchor present and resolved (§3.1) | **RED → GREEN** |
| D — two consecutive targets before one table | Both `<index:tbl-target-a>` and `<index:tbl-target-b>` reported dangling (§4) | Compiles; both `<index:tbl-target-a>` and `<index:tbl-target-b>` anchors present and resolved (§3.1) | **RED → GREEN** |
| Control — caption-less table, no preceding target | Already passing pre-fix (`test_caption_less_control_table_not_figure_wrapped` PASSED, `test_no_duplicate_label_definition` PASSED — the bug never affected this shape) | Unchanged: still not figure-wrapped (`kind: table` count 4, control excluded), no duplicate label | **GREEN → GREEN (byte-invariance held)** |

---

## 5. Regression sweep

**Full suite.**

**Command:** `uv run pytest -q`

```
================== 821 passed, 1 skipped in 73.22s (0:01:13) ===================
```

`821` = the recorded pre-existing baseline of `812 passed, 1 skipped` (the full suite EXCLUDING
`tests/test_captioned_table_propagated_target_render_gate.py`, which is 100% clean at this
worktree's base commit, per this plan's `<measured_pre_fix_state>`) plus the `9` tests in that one
module, now all passing (§3). `812 + 9 = 821` — exact match, zero new failures anywhere else in
the suite.

**Existing table/figure gates, explicitly re-run.**

**Command:** `uv run pytest tests/test_pdf_render_gate.py tests/test_figure_propagated_target_render_gate.py -q`

```
============================== 38 passed in 6.60s ==============================
```

Both `TestCaptionedTableRenderGate` / `TestCaptionedTablePreFixBasisFailureProof` /
`TestTableInListItemRenderGate` (in `test_pdf_render_gate.py`) and plan 42-02's permanent figure
gate `TestFigurePropagatedTargetRenderGate` (in `test_figure_propagated_target_render_gate.py`)
stay green — 38/38, no regressions from the table-side call-ordering move.

**Lint / format / type checks.**

**Command:** `uv run black --check .`

```
All done! ✨ 🍰 ✨
211 files would be left unchanged.
```

**Command:** `uv run ruff check .` (run via `steam-run` — this NixOS worktree's Nix-store `ruff`
was unavailable to shim directly, so the venv's generic-linux `ruff` binary was run under
`steam-run`'s FHS wrapper; `steam-run uv run ruff --version` confirmed `ruff 0.15.20` executes
correctly before the real check ran)

```
All checks passed!
```

**Command:** `uv run mypy typsphinx/`

```
Success: no issues found in 6 source files
```

All three exit `0`.

---

## 6. Scope statement

This file discharges SC#3 (a captioned table preceded by a standalone target compiles, and BOTH
labels resolve, with no duplicate-label fatal) and SC#5's GREEN half (the fix landed in a
separate, later commit than the recorded RED, proven by ancestry — § 1). It does NOT discharge:

- **The caption-less byte-invariance proof (SC#4 / D-04)** — an empty two-build diff between a
  named pre-fix commit and a named post-fix commit — owned by **plan 42-05**.
- **The repo-wide misrouting sweep (D-06 / D-07)** — already recorded, independently of this
  file, in **`42-GATE-EVIDENCE-03.md`** (plan 42-03, wave 1) — its sole finding was this same
  `depart_table` defect, now fixed here; the image-path half was a null result.
- **The Phase 41 release-prep reconciliation (SC#6)** — the CHANGELOG TBL-03 line and the
  re-measured SC#4 invariant sweep — owned by **plan 42-06**.

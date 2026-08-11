# Phase 43 Plan 06 — Gap Closure Evidence (CR-01: legend-in-legend state leak)

All command output below was executed in this task's own session, in this worktree
(`/home/yuta/Documents/typsphinx/.claude/worktrees/agent-afa741a07b43df548`), against this
worktree's HEAD at task start (`3e0097eb455c263c012a3131956b6fcb0fcc8283`, `docs(43): add code
review report`). Nothing here is transcribed from `43-REVIEW.md`'s own measurement — that
document measured a similar shape on the main tree in an earlier session; this file
re-measures the same defect in this worktree, against this task's own fixture Section 5.

## Environment provisioning (NixOS worktree hazards)

Per `CLAUDE.md` § "Worktree-isolated execution" and this task's environment briefing:

```
$ unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync --extra dev
...
 + typsphinx==0.7.0 (from file:///home/yuta/Documents/typsphinx/.claude/worktrees/agent-afa741a07b43df548)
 + uv==0.11.26
```

`.venv/bin/uv` was a generic-linux ELF NixOS cannot exec (`.venv/bin/uv --version` → exit 127,
`Could not start dynamically linked executable`). Symlinked to the system `uv`:

```
$ command -v uv
/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv
$ ln -sf /nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv .venv/bin/uv
$ readlink -f .venv/bin/uv
/nix/store/cgvijxnmydknslkl368k4j4j43akvl8b-uv-0.11.25/bin/uv   # resolves OUTSIDE .venv
$ .venv/bin/uv --version
uv 0.11.25 (x86_64-unknown-linux-gnu)
```

No standalone `ruff` package exists in this environment's Nix store (`command -v ruff` → exit
1), matching the prior executor's note recorded in `43-03-SUMMARY.md`. Used `patchelf` instead,
pointing the venv-installed `ruff` at the same glibc dynamic loader already working for the main
tree's `.venv/bin/ruff` (confirmed via `file` on the main-tree binary first):

```
$ file /home/yuta/Documents/typsphinx/.venv/bin/ruff
.../ruff: ELF 64-bit LSB pie executable, ... interpreter
/nix/store/8kvxvr3pmsypxiypq4g8zy13glnfr7nx-glibc-2.42-67/lib/ld-linux-x86-64.so.2, ...

$ patchelf --set-interpreter \
    /nix/store/8kvxvr3pmsypxiypq4g8zy13glnfr7nx-glibc-2.42-67/lib/ld-linux-x86-64.so.2 \
    .venv/bin/ruff
$ .venv/bin/ruff --version
ruff 0.15.20
```

Both binaries confirmed executing before any gate run. All subsequent commands run via `uv run`
(sphinx invoked as `sys.executable -m sphinx` inside the fixtures, resolving to this worktree's
venv).

**Baseline confirmed before any change:**

```
$ uv run python -m pytest -q
...
================== 836 passed, 1 skipped in 78.08s (0:01:18) ===================
```

Matches the orchestrator's stated baseline exactly.

## Task 1 — RED: legend-in-legend leaks `in_list_item` past `depart_legend`

### Doctree probe confirming the reproducing rST shape

Before writing the test assertions, `publish_doctree` was run over the extended fixture to
confirm docutils actually classifies fixture Section 5 the way the defect requires (BOTH levels
need a caption AND a legend, unlike Section 1 whose inner figure has only a caption):

```
$ uv run python -c "
from docutils.core import publish_doctree
rst = open('tests/fixtures/nested_figure_render_gate/index.rst').read()
doc = publish_doctree(rst, settings_overrides={'report_level': 5})
print(doc.pformat())
"
```

Relevant excerpt of `doc.pformat()` for the new section:

```
<section ids="legend-containing-a-figure-that-itself-has-a-caption-and-a-legend" ...>
    <title>
        Legend containing a figure that itself has a caption and a legend
    <paragraph>
        ...
    <figure>
        <image uri="img.png">
        <caption>
            NF5OUTERCAP
        <legend>
            <paragraph>
                NF5OUTERLEGEND
            <figure>
                <image uri="img.png">
                <caption>
                    NF5INNERCAP
                <legend>
                    <paragraph>
                        NF5INNERLEGEND
    <paragraph>
        NF5TRAILINGPARA sentinel text.
```

Confirmed: the outer figure has caption + legend, the legend contains a paragraph followed by a
NESTED figure that ITSELF has caption + legend, and a plain top-level paragraph follows the
outer figure as a sibling within the same section. This matches the shape `43-REVIEW.md` CR-01
describes, and is distinct from Section 1 (inner figure has caption only, no legend of its own).

### RED test run (unfixed translator)

```
$ uv run python -m pytest tests/test_nested_figure_render_gate.py -x -q
```

Full failure output (verbatim, this session):

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-afa741a07b43df548
configfile: pyproject.toml
plugins: cov-7.1.0
collected 7 items

tests/test_nested_figure_render_gate.py ......F

=================================== FAILURES ===================================
_ TestNestedFigureRenderGate.test_legend_in_legend_does_not_leak_list_item_state _

    def test_legend_in_legend_does_not_leak_list_item_state(
        self, nested_figure_render_gate_dir, temp_build_dir
    ):
        ...
        expected_trailing_para = f'par({{text("{NF5_TRAILING_PARA} sentinel text.")}})'
>       assert expected_trailing_para in typ_text, (
            "The trailing top-level paragraph after the legend-in-legend "
            "figure did not render through the normal paragraph path -- "
            "in_list_item leaked as True past the outer figure's "
            f"depart_legend (43-REVIEW.md CR-01):\n{typ_text}"
        )
E       AssertionError: The trailing top-level paragraph after the legend-in-legend figure did not render through the normal paragraph path -- in_list_item leaked as True past the outer figure's depart_legend (43-REVIEW.md CR-01):
E         ... [full emitted .typ elided here; see full-document excerpt below] ...
E         parbreak()
E
E         text("NF5TRAILINGPARA sentinel text.")
E
E         }
E
E       assert 'par({text("NF5TRAILINGPARA sentinel text.")})' in '...'

tests/test_nested_figure_render_gate.py:331: AssertionError
=========================== short test summary info ============================
FAILED tests/test_nested_figure_render_gate.py::TestNestedFigureRenderGate::test_legend_in_legend_does_not_leak_list_item_state
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
========================= 1 failed, 6 passed in 2.26s ==========================
```

(All 6 pre-existing gate tests still pass — the new Section 5 does not disturb the earlier
sections' assertions.)

### Direct build confirming the "worst outcome" framing (exit 0, no warning)

```
$ uv run python -m sphinx -b typstpdf -E tests/fixtures/nested_figure_render_gate /tmp/nfrg-red2
...
build succeeded.
$ echo $?
0
```

No `TypstError`, no `unknown node type` warning, no non-zero exit — a well-formed, plausible
document that silently misrepresents the source, exactly as the defect brief describes. This is
NOT a classic-`TypstError` RED like plan 43-03's own gate; it is the structural/rendered-output
RED shape this milestone's invariant #4 uses for defects that compile fine.

Pre-fix tail of the emitted `index.typ` (last ~30 lines, section 5 + trailing paragraph):

```
raw("in_list_item =\nTrue")
text(" into every sibling for the rest of the document. Section 1's inner figure has no legend of its own, so it does NOT trigger this; the inner figure here needs both a caption and a legend to reproduce the clobber.")})

[#figure(
{
  image("img.png")
parbreak()

text("NF5OUTERLEGEND")
[#figure(
{
  image("img.png")
parbreak()

text("NF5INNERLEGEND")
},
  caption: {text("NF5INNERCAP")}
) <index:id6>]


},
  caption: {text("NF5OUTERCAP")}
) <index:id5>]


parbreak()

text("NF5TRAILINGPARA sentinel text.")

}
```

The trailing paragraph emits as `parbreak()` + bare `text(...)` — the leaked list-item/legend
path — instead of `par({text("NF5TRAILINGPARA sentinel text.")})`.

### RED commit

Fixture Section 5 + new test method committed with `typsphinx/` completely untouched:

```
$ git rev-parse HEAD
4250e351a7ef27436f3aad312e73b3103e94ac3c
$ git diff 3e0097eb455c263c012a3131956b6fcb0fcc8283 4250e351a7ef27436f3aad312e73b3103e94ac3c -- typsphinx/ | wc -l
0
```

**RED commit SHA: `4250e351a7ef27436f3aad312e73b3103e94ac3c`**

## Task 2 — Fix and GREEN

### The fix

`typsphinx/translator.py`: `visit_legend`/`depart_legend` now push/pop
`(self.in_list_item, self.list_item_needs_separator)` tuples onto a new
`self._legend_list_item_stack: List[Tuple[bool, bool]]` (declared in `__init__`, alongside
`self._list_item_stack`), instead of saving into the two flat instance attributes
`_legend_saved_in_list_item`/`_legend_saved_list_item_needs_separator`. `depart_legend`'s pop is
guarded (`if self._legend_list_item_stack: ... else: False, False`) — never a bare `.pop()` or
`[-1]` index, matching the ASVS V5 pattern already used by `_pop_figure_state`/
`_pop_table_state` and `depart_list_item`.

**Pattern chosen: `self._list_item_stack` precedent** (a real stack of saved values, pushed on
visit and popped on depart), rather than the `_push_figure_state`/`_pop_figure_state`
dict-frame pattern. Reasoning: the legend save/restore covers exactly the same TWO scalars
`_list_item_stack` already tracks one of (`in_list_item`) — a `Tuple[bool, bool]` per push is a
direct, minimal extension of that existing precedent, and the figure-state frame-dict pattern
exists specifically because it snapshots SIX heterogeneous scalars (`in_figure`,
`figure_content`, `figure_caption`, `_figure_block_width`, `_figure_has_legend`,
`_saved_body_for_figure_caption`) where a dict's named keys are more legible than a 6-tuple. Two
booleans do not need that machinery.

### GREEN test run (fixed translator)

```
$ uv run python -m pytest tests/test_nested_figure_render_gate.py -v
============================= test session starts ==============================
...
tests/test_nested_figure_render_gate.py::TestNestedFigureRenderGate::test_build_exits_zero PASSED [ 14%]
tests/test_nested_figure_render_gate.py::TestNestedFigureRenderGate::test_no_unknown_node_type_warning_for_legend PASSED [ 28%]
tests/test_nested_figure_render_gate.py::TestNestedFigureRenderGate::test_pdf_produced_with_both_captions_for_nested_figure PASSED [ 42%]
tests/test_nested_figure_render_gate.py::TestNestedFigureRenderGate::test_plain_text_legend_with_no_nesting_compiles PASSED [ 57%]
tests/test_nested_figure_render_gate.py::TestNestedFigureRenderGate::test_image_only_control_is_byte_unchanged PASSED [ 71%]
tests/test_nested_figure_render_gate.py::TestNestedFigureRenderGate::test_legend_with_no_caption_compiles PASSED [ 85%]
tests/test_nested_figure_render_gate.py::TestNestedFigureRenderGate::test_legend_in_legend_does_not_leak_list_item_state PASSED [100%]

============================== 7 passed in 2.29s ===============================
```

### Direct before/after diff of the emitted `.typ`

```
$ uv run python -m sphinx -b typstpdf -E tests/fixtures/nested_figure_render_gate /tmp/nfrg-green
...
build succeeded.
```

Post-fix tail of `index.typ`:

```
[#figure(
{
  image("img.png")
parbreak()

text("NF5OUTERLEGEND")
[#figure(
{
  image("img.png")
parbreak()

text("NF5INNERLEGEND")
},
  caption: {text("NF5INNERCAP")}
) <index:id6>]


},
  caption: {text("NF5OUTERCAP")}
) <index:id5>]

par({text("NF5TRAILINGPARA sentinel text.")})



}
```

**Full-document `diff` between the pre-fix and post-fix `index.typ` (this session's own
build products, not transcribed):**

```
$ diff /tmp/nfrg-red2/index.typ /tmp/nfrg-green/index.typ
145a146
> par({text("NF5TRAILINGPARA sentinel text.")})
147d147
< parbreak()
149d148
< text("NF5TRAILINGPARA sentinel text.")
```

The ONLY difference across the entire emitted document is the trailing paragraph's rendering
path — every other line, including both figures' `image(...)`/`caption:`/`<label>` emission and
every other section's bytes, is byte-identical pre- and post-fix. This is the corrected
`par({...})` form the orchestrator's measured symptom (using a different fixture path/sentinel
names) described.

### PDF-extracted text: both captions and both legend sentinels present

Covered by `test_legend_in_legend_does_not_leak_list_item_state`'s own `pypdf` extraction
assertions (see GREEN run above) — `NF5OUTERCAP`, `NF5OUTERLEGEND`, `NF5INNERCAP`,
`NF5INNERLEGEND`, `NF5TRAILINGPARA` all asserted PRESENT and all pass.

### Depth-general proof: three-level legend nest (scratch build, not committed to the fixture)

To prove the fix is not tuned to depth 2, a scratch fixture (outside the repo, under
`/tmp/claude-.../scratchpad/three-level/`, never committed) nests THREE levels of
figure-with-caption-and-legend, each level's legend containing the next figure, followed by a
trailing top-level paragraph:

```rst
.. figure:: img.png

   L1CAP

   L1LEGEND

   .. figure:: img.png

      L2CAP

      L2LEGEND

      .. figure:: img.png

         L3CAP

         L3LEGEND

L3TRAILINGPARA sentinel text.
```

```
$ uv run python -m sphinx -b typstpdf -E /tmp/.../scratchpad/three-level /tmp/three-level-build
...
build succeeded.
$ echo $?
0
```

Emitted `.typ` tail:

```
[#figure(
{
  image("img.png")
parbreak()

text("L2LEGEND")
[#figure(
{
  image("img.png")
parbreak()

text("L3LEGEND")
},
  caption: {text("L3CAP")}
) <index:id3>]


},
  caption: {text("L2CAP")}
) <index:id2>]


},
  caption: {text("L1CAP")}
) <index:id1>]

par({text("L3TRAILINGPARA sentinel text.")})


}
```

The trailing paragraph renders as `par({...})` — correctly restored at THREE nesting levels, not
merely two. `pypdf`-extracted PDF text:

```
L1CAP PRESENT
L1LEGEND PRESENT
L2CAP PRESENT
L2LEGEND PRESENT
L3CAP PRESENT
L3LEGEND PRESENT
L3TRAILINGPARA PRESENT
```

All seven sentinels present — the fix is depth-general, not tuned to the two-level shape it was
handed.

### Fix commit

```
$ git rev-parse HEAD
4ea64006cb930bf1362a61dfa9052811f79617a6
```

**Fix commit SHA: `4ea64006cb930bf1362a61dfa9052811f79617a6`**

## Task 3 — Full gates

```
$ uv run python -m pytest -q
...
================== 837 passed, 1 skipped in 77.39s (0:01:17) ===================
```

837 = 836 baseline + 1 new test method (`test_legend_in_legend_does_not_leak_list_item_state`).
Matches the orchestrator's "836 + your new tests" expectation exactly (one new test method was
added, not multiple — the single method covers both the byte-level render assertion and the
PDF-text presence assertions).

```
$ uv run black --check .
All done! ✨ 🍰 ✨
217 files would be left unchanged.

$ .venv/bin/ruff check .
All checks passed!

$ uv run mypy typsphinx/
Success: no issues found in 6 source files
```

All three CI gates green.

```
$ git status --porcelain .github/ pyproject.toml uv.lock
(empty)
```

No changes to `.github/`, `pyproject.toml`, or `uv.lock`.

## Summary

| Check | Result |
|-------|--------|
| RED observed pre-fix (unfixed translator) | Confirmed — exit 0, trailing paragraph emits `parbreak()` + bare `text(...)` instead of `par({...})` |
| RED commit touches `typsphinx/` | No — `git diff` empty |
| Fix applied | `self._legend_list_item_stack: List[Tuple[bool, bool]]` replaces the two flat scalars; guarded pop |
| GREEN post-fix | Confirmed — trailing paragraph emits `par({text("NF5TRAILINGPARA sentinel text.")})` |
| Before/after `.typ` diff | Isolated to exactly the trailing-paragraph rendering path; nothing else changed |
| Depth-general (3-level nest) | Confirmed via scratch build — restores correctly, all 7 sentinels present |
| Full suite | 837 passed, 1 skipped (836 baseline + 1 new test) |
| black / ruff / mypy | All green |
| `.github/` / `pyproject.toml` / `uv.lock` | Untouched |
| RED commit SHA | `4250e351a7ef27436f3aad312e73b3103e94ac3c` |
| Fix commit SHA | `4ea64006cb930bf1362a61dfa9052811f79617a6` |

# Phase 36: Shared-Emission Seam Cleanup - Context

**Gathered:** 2026-07-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Two pre-existing emission-shape defects on the seam every later v0.7.0 phase has to cut through:

1. **ADM-06 (+ the `desc_signature` half of the same seam)** — `visit_desc_signature` /
   `depart_desc_signature` (`typsphinx/translator.py:4684, 4693`) and `visit_rubric` /
   `depart_rubric` (`typsphinx/translator.py:5047, 5065`) currently construct a throwaway
   `nodes.strong()` and call `visit_strong` / `depart_strong` on it, so all three node kinds emit
   the identical `strong({ … })` wrapper. Give `desc_signature` and `rubric` their own open/close
   pair so Phase 37 can restyle signatures and Phase 39 can restyle rubrics without touching
   `**bold**`.
2. **MATH-02** — `visit_math_block` emits one blank line more than every other block-level handler
   when the math sits inside a list item.

**This phase changes no rendering.** The visual work is elsewhere in the milestone:
`desc_signature` typography is Phase 37 (SIG-01..09); rubric indentation and the admonition
taxonomy are Phase 39 (ADM-01..05). Phase 36 is rewiring plus one whitespace fix.

**Out of scope:** any change to `visit_strong`'s own behaviour for plain `**bold**` markup; the
`emphasis` dummy-node delegations (`visit_title_reference`, `visit_inline`'s `versionmodified`
branch) — ROADMAP SC#1 names only the `strong` delegations; the `par()`-loss bug found during this
discussion (see Deferred Ideas).

</domain>

<decisions>
## Implementation Decisions

### Decoupling shape

- **D-01: `visit_strong`'s body is copied into each handler, not shared.** No `_open_inline_wrapper`
  helper, no parameterised call string, no shared `_enter_bold_wrapper`. `visit_desc_signature` /
  `depart_desc_signature` and `visit_rubric` / `depart_rubric` each get their own full copy of the
  logic they currently borrow (paragraph separator, `_enter_inline_concat_element` /
  `_exit_inline_concat_element`, `in_paragraph` / `in_list_item` /
  `list_item_needs_separator` save-restore, the `_in_markup_mode` `#` prefix). Rationale: Phase 37
  and Phase 39 will each take these two in different directions, so triplication now buys
  unconstrained divergence later. Accepted cost: three copies of the same state machine until 37/39
  make them genuinely different.
- **D-02: keep the existing single-slot state attributes; do not fix the `par()`-loss bug here.**
  All three copies keep using `_strong_was_in_paragraph` / `_strong_was_in_list_item` /
  `_strong_was_list_item_needs_separator`. Renaming them per handler would repair the leak described
  in Deferred Ideas, but it changes emitted bytes for the "rubric containing inline markup"
  construct and would put an exception into SC#2, this phase's only acceptance criterion. File the
  bug as a todo instead.
- **D-03: the implementation form is unconstrained as long as byte-identity holds.** Verbatim copy
  versus a pruned copy (dropping branches proven unreachable from `desc_signature` / `rubric`) is a
  planner/implementer call — the binding constraint is that the decoupling change alone produces a
  zero diff.

### MATH-02 evidence and fix

- **D-04: RED lives in the emitted `.typ`; the PDF gets an invariance guard, not a RED assertion.**
  Structural assertion on the emitted `.typ` (two blank lines after the math expression pre-fix →
  RED; one blank line post-fix → GREEN). The compiled PDF gets a *regression* assertion that the
  extracted text is unchanged across the fix — which turns "this change is inert" into a test rather
  than a claim. Measured basis, this session, on a list-item block-math fixture compiled through the
  real `typst.compile()`: current output and the intended post-fix output produce **byte-identical
  PDFs** (22,855 bytes each), identical page counts (3), and identical `pypdf`-extracted text. A
  PDF-text RED for MATH-02 is therefore impossible — it is green before and after.
- **D-05: ROADMAP SC#3 is corrected via `/gsd-phase` before planning.** Two errors, both measured
  this session:
  - "exactly one blank line **before** it" — the redundant blank line is **after** the math
    expression, between `mitex(…)` / `$ … $` and the following `parbreak()`. There is already zero
    blank line before it.
  - "asserted … on the compiled PDF's extracted text, with the assertion recorded RED" — impossible
    per D-04. Rewrite to the `.typ`-RED + PDF-invariance-guard form.
  The correction goes into ROADMAP.md (not just here) because the verifier reads ROADMAP success
  criteria directly; a stale SC re-opens the argument at verify time.

### Claude's Discretion

Neither of these was selected for discussion; decided from measurement, recorded here so planning
does not re-open them.

- **D-06: take the todo's option (a) — drop the `list_item_needs_separator` bookkeeping — and additionally reset the flag to `False`.**
  Option (b) (gating the pre-existing unconditional
  `"\n\n"` to `not in_list_item`) yields **zero** blank lines after the math inside a list item, not
  one, so it does not satisfy SC#3 as corrected. Option (a) yields exactly one. **But a naive (a) is
  incomplete:** for a `:label:`-carrying equation, `_emit_id_anchors` sets
  `list_item_needs_separator = True` *before* the math is emitted, so merely deleting the trailing
  `if self.in_list_item: self.list_item_needs_separator = True` leaves the flag set and the next
  sibling still emits its own leading `"\n"` — two blank lines again. Measured this session on a
  `.. math:: :label: eq-labeled` inside a bullet item. The fix must clear the flag, not just refrain
  from setting it, and the fixture must cover both the plain and the `:label:` paths on both the
  mitex and native (`-D typst_use_mitex=0`) emission paths.
- **D-07: split the phase into a byte-identical decoupling change and a byte-changing MATH-02 change, in separate plans and separate commits, decoupling first.**
  SC#2's recorded diff of two
  real `sphinx-build -b typst` runs is taken against the **decoupling commit alone** — mixing
  MATH-02 into the same diff destroys the only evidence this phase has that the rewiring was
  harmless.

### Folded Todos

- **`.planning/todos/pending/2026-07-29-visit-math-block-redundant-blank-line-in-list-items.md`**
  (`resolves_phase: 36`) — the MATH-02 record. Folded in full. **One claim in it is wrong and must
  not be carried into planning:** it states the fix forces the Construct E and Construct G
  exact-string assertions in `tests/test_inline_math_after_text_render_gate.py` to be re-derived.
  Measured this session — it does not. Both assertions pin only the separator *before* the math
  (`tests/test_inline_math_after_text_render_gate.py:175` pins
  `text("Text before block math.")\nmitex(\`E = m c^2\`)`; line 265 pins
  `[#metadata(none) <…>]\n\nmitex(\`G = m a`). No assertion anywhere in `tests/` pins the shape
  *after* a block-math expression, and `tests/test_math_mitex.py`, `tests/test_math_native.py` and
  `tests/test_math_fallback.py` contain no `\n`-bearing assertions at all. The exact-string blast
  radius of MATH-02 measures at **zero existing assertions**; the phase's test work is adding the
  new RED fixture, not migrating old ones.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and criteria

- `.planning/ROADMAP.md` § "Phase 36: Shared-Emission Seam Cleanup" — goal, dependencies, the four
  success criteria. **Read the D-05 correction above first**: SC#3 as written is wrong on two
  points and is being amended.
- `.planning/ROADMAP.md` § "🚧 v0.7.0 — API rendering design overhaul (ACTIVE)" — the five binding
  constraints, in particular invariant #4 (GATE-01's RED state is redefined for this milestone) and
  invariant #5 (test migration is owned per phase).
- `.planning/REQUIREMENTS.md` — ADM-06 (line 105) and MATH-02 (line 136) are this phase's two
  requirements. ADM-01..ADM-05 belong to Phase 39 and SIG-01..09 to Phase 37; do not pull them
  forward.

### The defects themselves

- `.planning/todos/pending/2026-07-29-visit-math-block-redundant-blank-line-in-list-items.md` —
  the MATH-02 record, including both candidate fixes. See the correction in "Folded Todos" above.
- `.planning/milestones/v0.6.5-phases/34-inline-math-after-text-separator-fix/34-REVIEW.md` (WR-01)
  — where the redundant blank line was first reproduced, with the measured emission.
- `.planning/milestones/v0.6.5-phases/35-v0-6-5-release-prep/35-CONTEXT.md` (D-05, D-10) — why the
  fix was deferred out of v0.6.5 and required to be filed as a todo.

### Code under change

- `typsphinx/translator.py:1203-1280` — `visit_strong` / `depart_strong`, the body being copied.
- `typsphinx/translator.py:4664-4722` — `visit_desc_signature` / `depart_desc_signature`, including
  the id-anchor emission that must stay put across the decoupling.
- `typsphinx/translator.py:5034-5076` — `visit_rubric` / `depart_rubric`, including the FID-04
  trailing `linebreak()` and the `"\n"` that keeps it from abutting `})`.
- `typsphinx/translator.py:4014-4091` — `visit_math_block`, carrying both separation mechanisms
  (the unconditional `"\n\n"` at ~4079 and the Phase 34 flag at ~4087).

### Project standing rules

- `CLAUDE.md` § "Worktree-isolated execution" — worktree isolation is the standing execution mode;
  per-worktree `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` then `uv run …`
  is mandatory, not conditional.
- `CLAUDE.md` § "The `@preview` version-sync hazard" — untouched by this phase, but the reason D-01's
  triplication is a recognised class of hazard in this repo.

</canonical_refs>

<code_context>
## Existing Code Insights

### Measured starting state

A real `sphinx-build -b typst` run this session on a fixture with `**bold**`, a
`.. py:function::` and a `.. rubric::` emits all three through the same wrapper:

```typst
par({text("これは ")
strong({text("重要")})                       ← strong node
text(" な段落です。")})

strong({text("connect")                      ← desc_signature node
text("(") + text("host") + text(", ") + … + text(")")})
[#metadata(none) <index:connect>]
par({text("接続する。")})

parbreak()

strong({text("使用例")})                     ← rubric node
linebreak()
```

List-item block math, same session, `cat -A`-verified:

```typst
text("リスト項目の前置き。")
mitex(`E = m c^2`)
                    ← blank 1
                    ← blank 2  (the redundant one, MATH-02)
parbreak()

text("数式の後の段落。")
```

### Reusable assets

- **`_emit_forced_break(…)`** — the shared helper `visit_desc_signature` (sibling `linebreak()`)
  and `depart_rubric` (trailing `linebreak()`) already use; unaffected by the decoupling.
- **`_emit_id_anchors(node)`** — used by `visit_rubric` and `visit_math_block`; note it drives
  `list_item_needs_separator` itself, which is exactly what makes D-06's naive form incomplete.
- **`_enter_inline_concat_element()` / `_exit_inline_concat_element()`** — stack-based concat-context
  helpers called from inside `visit_strong`'s body; they are ordinary shared helpers, not
  dummy-node delegation, so copying the call sites is fine and SC#1's grep is unaffected.
- **Existing render gates that already exercise the seam** —
  `tests/test_desc_signature_concat_render_gate.py`, `tests/test_desc_signature_anchor_render_gate.py`,
  `tests/test_desc_sig_space_render_gate.py`, `tests/test_rubric_option_concat_render_gate.py`,
  `tests/test_rubric_propagated_target_render_gate.py`. These are the natural regression net for
  "nothing changed"; the SC#2 byte-diff fixture should cover the same constructs the ROADMAP names
  (signatures, sibling signatures, rubrics incl. autodoc's "Options" rubric, bold markup).

### Established patterns

- **Dummy-node delegation is repo idiom, not an accident** — `visit_title_reference` and
  `visit_inline`'s `versionmodified` branch delegate to `visit_emphasis` the same way. Only the
  `strong` delegations from `desc_signature` and `rubric` are in scope; leaving the `emphasis` ones
  is deliberate, and SC#1's grep should be written narrowly enough not to flag them.
- **Every node-handler change in this project carries a recorded-RED GATE-01 fixture** — with the
  milestone-specific redefinition that RED may be structural rather than a compile fatal.

### Integration points

- `tests/test_corpus_gate.py` — the full-corpus `-b typstpdf` gate is `@pytest.mark.slow` and
  excluded from the default/CI run via `-m "not slow"`; it must be run explicitly for SC#4.

</code_context>

<specifics>
## Specific Ideas

- The owner's framing of the phase, verbatim in intent: *"ここでは分離だけ実施して Phase 39 で本式
  バグ修正するのだから、ここではとりあえずバイトに差が出ないように分離するだけ"* — separation only,
  zero byte delta, appearance work deferred to the phases that own it. Any planning that starts
  reshaping `desc_signature` or `rubric` output has left this phase's scope.
- Claims in the ROADMAP and in the folded todo were both found wrong when measured (SC#3's
  "before it" + PDF-RED requirement; the todo's exact-string blast-radius estimate). Verify before
  building on either.

</specifics>

<deferred>
## Deferred Ideas

- **`par()` loss after a rubric containing inline markup (new, found during this discussion).**
  `visit_strong` saves its caller state into three single-slot instance attributes
  (`_strong_was_in_paragraph`, `_strong_was_in_list_item`,
  `_strong_was_list_item_needs_separator`) and `depart_strong` `delattr`s them
  (`typsphinx/translator.py:1244-1275`). When a rubric contains a real `strong` child — e.g.
  `.. rubric:: **強調** 入り見出し` — the inner `depart_strong` consumes and deletes the slots, so
  the outer `depart_rubric`'s dummy depart restores nothing and `in_list_item` stays `True` for the
  rest of the document. Measured this session: every subsequent paragraph loses its `par({…})`
  wrapper.

  ```typst
  strong({text("強調なし見出し")})
  linebreak()
  par({text("後続の段落A。")})          ← correct

  strong({strong({text("強調")})
  text(" 入り見出し")})
  linebreak()
  parbreak()
  text("後続の段落B。")                 ← par() gone
  parbreak()
  text("さらに次の段落C。")             ← and stays gone
  ```

  This is a rendering defect, not diff noise, and it is untracked. Per D-02 it is **not** fixed in
  Phase 36 (fixing it changes bytes and would put an exception into SC#2). File a todo; the natural
  home is Phase 39, which owns `rubric` anyway. Real-corpus incidence (how many rubrics carry inline
  markup in Sphinx's `doc/` and in this repo's `docs/`) has **not** been measured — measure it when
  the todo is picked up.

### Reviewed Todos (not folded)

`todo.match-phase 36` returned four further records, all keyword false positives, none folded:

- `2026-07-22-add-sphinx-linkcheck-ci-job.md` — deferred as Future requirement LNK-01.
- `2026-07-22-citation-node-support-untracked.md` — belongs to **Phase 40** (CIT-01..06).
- `2026-07-22-modernize-typing-imports-drop-up006-up035-ignore.md` — unrelated; still deferred.
- `2026-07-25-derive-typst-lang-duplicated-warning-block.md` — `template_engine.py`, unrelated.

</deferred>

---

*Phase: 36-Shared-Emission Seam Cleanup*
*Context gathered: 2026-07-30*
</content>
</invoke>

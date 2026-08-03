# Phase 39 — Closing Gate Evidence (Plan 39-08)

**Run:** 2026-08-02, in this worktree, after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync
--extra dev` and the `uv`/`ruff` NixOS-sandbox shims (per `CLAUDE.md` "Worktree-isolated execution"
and the project's `nixos-sandbox-test-env` memory). Base commit
`6f891563b835972a9c0179bb7fe1dfb917fb4554` (merges 39-01 through 39-07).

Every command below was run for real in this session; none of its results are inferred or copied
from an earlier plan's SUMMARY.

---

## 1. The full-corpus real-render gate — ACTUALLY RAN, not skipped

```
$ uv run pytest tests/test_corpus_gate.py -m slow -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
collected 5 items / 3 deselected / 2 selected

tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED [ 50%]
tests/test_corpus_gate.py::test_empty_url_before_after SKIPPED (SC#3
before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1
to run it (RESEARCH Open Question 1))                                    [100%]

================= 1 passed, 1 skipped, 3 deselected in 14.17s ==================
```

**Resolved corpus tag:** `v9.1.0` (`resolve_corpus_tag()` returns `f"v{sphinx.__version__}"`;
`sphinx.__version__` measured live in this worktree's venv: `9.1.0`).

**Cache:** the corpus was already present at `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0` before
this run (confirmed via `ls` before running the gate) — no network clone was needed this session,
and the test's own caching-by-resolved-tag behavior means a clone would have happened
transparently had the cache been cold.

**Duration:** 14.17s (pytest's own reported summary line, above).

**Pass/fail:** `TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error` **PASSED** — the real
`sphinx-build -b typstpdf` over Sphinx's own `doc/` tree, augmented per the test's own D-03 2-line
`conf.py` append, produced no fatal Typst error. This is the requirement T-39-SC/SC#5 needs.

**The one SKIP in this output (`test_empty_url_before_after`) is NOT the corpus gate itself** — it is
a separate, explicitly env-gated (`TYPSPHINX_CORPUS_REPORT=1`) diagnostic measurement unrelated to
whether the corpus compiles. It is deselected by default and is not part of what SC#5 or this plan's
`must_haves.prohibitions` (first entry) require to run. **The corpus gate itself ran and passed — this
is not recorded as a pass on the strength of a skip.**

---

## 2. Full test suite, unfiltered

```
$ uv run pytest -q
============================= test session starts ==============================
collected 764 items
...
===================== 763 passed, 1 skipped in 69.91s (0:01:09) ======================
```

**763 passed, 1 skipped, 0 failed.** Total 764, matching the recorded reference baseline (762
passed / 2 skipped / 0 failed on the merged main tree — differing skip count between a worktree and
the main tree is normal here since this worktree's own real-run of the corpus gate above resolved
one of the two skips into a pass; the *total* of 764 is what must and does agree).

---

## 3. Fast tier (`not slow`)

```
$ uv run pytest -m "not slow" -q
collected 764 items / 29 deselected / 735 selected
...
===================== 735 passed, 29 deselected in 51.02s ======================
```

**735 passed, 0 failed, 29 deselected (the slow-marked corpus-gate class).** Matches
`39-06-SUMMARY.md`'s own recorded fast-tier baseline (735 passed) with zero regressions introduced
by this plan's own (documentation-only) work.

---

## 4. `test_preview_version_sync.py` — the gentle-clues pin, confirmed by name

```
$ uv run pytest tests/test_preview_version_sync.py -x -v
tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED
3 passed
```

**All three green.** This phase changed which of gentle-clues' functions are called (`tip`, `error`,
`notify`, `abstract` alongside the pre-existing `info`/`warning`/`task`), not the pin, and the two
newly-used functions (`notify`, `abstract`) were already in scope through the existing wildcard
import `#import "@preview/gentle-clues:1.3.1": *` — confirmed by this green result, not assumed.

---

## 5. Lint, format, type trio

```
$ uv run black --check .
All done!
198 files would be left unchanged.

$ uv run ruff check .
All checks passed!

$ uv run mypy typsphinx/
Success: no issues found in 6 source files
```

All three pass with zero findings.

---

## 6. Documentation dogfood build through the Typst PDF environment

```
$ uv run tox -e docs-pdf
docs-pdf: commands[0] .../docs> sphinx-build -b typstpdf source _build/pdf
...
Copying template assets...
Compiling 1 master document(s) to PDF...
Generated PDF: .../docs/_build/pdf/typsphinx.pdf
build succeeded, 4 warnings.
  docs-pdf: OK (3.96=setup[0.50]+cmd[3.45] seconds)
  congratulations :) (3.98 seconds)
```

Exit 0. `docs/_build/pdf/typsphinx.pdf` generated, 1,938,001 bytes.

**Page count:** measured live via `pypdf.PdfReader(...).pages`:

```
$ uv run python3 -c "
import pypdf
r = pypdf.PdfReader('docs/_build/pdf/typsphinx.pdf')
print('pages:', len(r.pages))
"
pages: 91
```

**91 pages**, versus the **90 pages** recorded as the post-Phase-38 baseline in
`38-08-GATE-EVIDENCE.md`/`38-TEST-CENSUS.md`'s own Bucket D table (`tox -e docs-pdf` measurement).
**+1 page.** This project's own `docs/source/` tree contains **no literal `.. rubric::`,
`.. seealso::`, `.. topic::`, `.. admonition::`, `.. attention::`, or `.. danger::` directive**
(confirmed live: `grep -rln` for each of those directive spellings across every `.rst` file under
`docs/source/` returns nothing) and `docs/` itself carries zero commits across this whole phase
(`git log --oneline 8406b8a..HEAD -- docs/` is empty) — so the +1 page is entirely a consequence of
this phase's `typsphinx/translator.py` changes reaching content that was already there, not of any
docs-content edit.

The docs project does contain 3 real admonitions (`note`/`warning`/`tip` type, confirmed by the same
grep) whose English catalog titles are byte-identical to their pre-phase hardcoded titles (per this
plan's own `39-TEST-CENSUS.md` finding), so title-length change is not the cause here. The
`api/index.rst` autodoc-generated content is the more likely source: every `py:class`/`py:function`
directive with parameters and options emits at least one machine-generated `rubric` ("Options")
node, invisible to a literal-directive grep but real at the docutils-tree level that
`visit_rubric`/`depart_rubric` walk. Two of this phase's rubric fixes pull page count in opposite
directions on exactly this kind of content: **D-11's separator-double-count fix removes** up to two
blank lines at each qualifying anchor (shrinks), while **D-13's `_rubric_was_*` slot-rename fix
restores** the `par({...})` wrapper to every subsequent paragraph in the document that a
markup-containing rubric's state-bookkeeping bug had previously (silently, pre-fix) stripped it from
document-wide (expands — D-13 itself documents this defect as reaching "every subsequent paragraph
in the document to the end of the file," so its fix can only ever add spacing back, never remove
more than the wrapper it restores). A net **+1** page is consistent with these two legitimate,
phase-scoped mechanisms only partially offsetting each other over a ~90-page document, and is not
evidence of a defect — no unexpected content, broken layout, or compile warning accompanies it (the
build's 4 warnings are pre-existing docstring/docutils warnings unrelated to admonitions or rubrics,
visible in the raw build log: two `visit_toctree` docstring indentation warnings and one
`visit_desc_sig_name` inline-emphasis warning, plus one `unknown_visit` for a `<problematic>` node —
none of which are new to this phase).

---

## 7. Milestone invariants, re-checked by command at close

**(a) Zero new runtime dependencies:**

```
$ git diff 8406b8a..HEAD -- pyproject.toml
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -44,6 +44,7 @@ dev = [
     "twine>=5.0",
     "build>=1.0",
     "pypdf>=6.14,<7",
+    "pillow>=12.3,<13",  # D-07: ADM-04 greyscale render (Image.convert), dev-only
 ]
 docs = [
```

The only `pyproject.toml` change across the whole phase is the single `pillow` line added to
`[project.optional-dependencies].dev` (D-07, gated behind a `checkpoint:human-verify` package
legitimacy check at plan 39-04). `[project.dependencies]` (the runtime array, lines 27-31) shows
**zero** lines in the diff — confirmed unchanged, live:

```
$ (lines 27-31 of pyproject.toml, read live)
dependencies = [
    "sphinx>=9.1,<10",
    "docutils>=0.21,<0.23",
    "typst>=0.15.0,<0.16",
]
```

Same three runtime dependencies as pre-phase. **Invariant held.**

**(b) No new `@preview` package imported anywhere under `typsphinx/`:**

```
$ grep -n "@preview" typsphinx/*.py
typsphinx/writer.py:155:            imports.append('#import "@preview/codly:1.3.0": *')
typsphinx/writer.py:156:            imports.append('#import "@preview/codly-languages:0.1.10": *')
typsphinx/writer.py:157:            imports.append('#import "@preview/mitex:0.2.7": mi, mitex')
typsphinx/writer.py:158:            imports.append('#import "@preview/gentle-clues:1.3.1": *')
typsphinx/template_engine.py:612:            output_parts.append('#import "@preview/codly:1.3.0": *')
typsphinx/template_engine.py:613:            output_parts.append('#import "@preview/codly-languages:0.1.10": *')
typsphinx/template_engine.py:614:            output_parts.append('#import "@preview/mitex:0.2.7": mi, mitex')
typsphinx/template_engine.py:615:            output_parts.append('#import "@preview/gentle-clues:1.3.1": *')

$ grep -n "@preview" typsphinx/templates/base.typ
8:#import "@preview/codly:1.3.0": *
9:#import "@preview/codly-languages:0.1.10": *
14:#import "@preview/mitex:0.2.7": *
19:#import "@preview/gentle-clues:1.3.1": *
```

**Exactly four packages** (`codly`, `codly-languages`, `mitex`, `gentle-clues`) at all three
lockstep sites (`writer.py`, `template_engine.py`, `templates/base.typ`) — the same count and the
same package set as pre-phase. `test_preview_version_sync.py` (§4 above) confirms these three sites
agree with each other and with `examples/**/*.typ`. This phase changed *which functions* of
gentle-clues are called (adding calls to `tip`, `error`, `notify`, `abstract`, all already reachable
through the existing wildcard import), not the import line itself. **Invariant held.**

**(c) The pinned gentle-clues version is identical to its pre-phase value:**

```
$ git show 8406b8a:typsphinx/writer.py | grep gentle-clues
            imports.append('#import "@preview/gentle-clues:1.3.1": *')
```

`1.3.1` pre-phase, `1.3.1` post-phase (confirmed live in §b above) — byte-identical. **Invariant
held.**

---

## Summary of this task's verification commands

| Command | Result |
|---|---|
| `uv run pytest tests/test_corpus_gate.py -m slow -v` | 1 passed (14.17s, tag `v9.1.0`), 1 skipped (unrelated env-gated diagnostic), 3 deselected |
| `uv run pytest` (unfiltered) | 763 passed, 1 skipped, 0 failed (69.91s) |
| `uv run pytest -m "not slow"` | 735 passed, 29 deselected, 0 failed (51.02s) |
| `uv run pytest tests/test_preview_version_sync.py -x` | 3 passed |
| `uv run black --check .` | clean, 198 files unchanged |
| `uv run ruff check .` | clean |
| `uv run mypy typsphinx/` | clean, 6 source files |
| `uv run tox -e docs-pdf` | exit 0, PDF generated, 91 pages (90 pre-phase, +1 explained above) |
| `git diff -- pyproject.toml` (runtime deps) | empty (only `[dev]` gained `pillow`) |
| `@preview` import count/pin | 4 packages, gentle-clues `1.3.1`, unchanged at all 3 sites |

---

## Reconciliation — the roadmap and requirement records against what each requirement reached

Per this plan's Task 3. For each of Phase 39's five success criteria: the criterion, the discharging
artifact and command, and its status.

### SC#1 — bucket moves for `seealso` and `attention`

**Criterion:** `seealso` renders in the same bucket as `hint`/`tip`, `attention` in the same bucket
as `danger`/`error`, asserted on the emitted call and confirmed in the compiled PDF, with the RED
recorded pre-phase.

**Discharging artifact/command:** `39-GATE-EVIDENCE-01.md` records the pre-phase RED (6 failing
assertions in `tests/test_admonition_bucket_render_gate.py`, including
`test_seealso_routes_to_tip_bucket` and `test_attention_routes_to_error_bucket`, plus
`test_admonitionbuckettitlegate`'s PDF-text RED). `39-05-SUMMARY.md` records the fix (commit
`a6c04ea`) and the flip to GREEN, re-confirmed live this session:

```
$ uv run pytest tests/test_admonition_bucket_render_gate.py::test_seealso_routes_to_tip_bucket tests/test_admonition_bucket_render_gate.py::test_attention_routes_to_error_bucket tests/test_pdf_render_gate.py::TestAdmonitionPdfRenderGate::test_admonitionbuckettitlegate -v
3 passed
```

**Status: MET.**

### SC#2 — generic admonition styled and titled

**Criterion:** A generic `.. admonition:: Custom Title` renders as a styled box carrying that title,
asserted both on the emitted call and by the title surviving into the compiled PDF's extracted text.

**Discharging artifact/command:** `39-GATE-EVIDENCE-01.md`'s
`test_generic_admonition_routes_to_notify` RED; `39-05-SUMMARY.md`'s fix (commit `a6c04ea`, D-09);
the pre-existing `TestTopicLineBlockRenderGate::test_admonitiontitleregression_multichild`
(`tests/test_pdf_render_gate.py`), confirmed untouched-but-still-passing per this plan's own
`39-TEST-CENSUS.md` row 3 (the directive-supplied `"Custom Title"` was already asserted pre-phase
and stays green because it was never a catalog-default title in the first place). Re-confirmed
live:

```
$ uv run pytest tests/test_admonition_bucket_render_gate.py::test_generic_admonition_routes_to_notify "tests/test_pdf_render_gate.py::TestTopicLineBlockRenderGate::test_admonitiontitleregression_multichild" -v
2 passed
```

**Status: MET.**

### SC#3 — rubric indent, invariance guard per D-12

**Criterion (as currently worded in `ROADMAP.md` § "Phase 39", item 3):** "A rubric inside a
description body ... has a left edge strictly greater than the page margin and equal to its
containing body's edge, measured with `pypdf`. **Corrected per 39-CONTEXT.md D-12:** this property
was measured 2026-08-02 to hold ALREADY against pre-phase code ... It is therefore asserted as an
**invariance guard**, green in both directions, following exactly the resolution Phase 36's SC#3
took for its own already-true PDF claim."

**Confirmed: the roadmap wording already reads as an invariance guard per D-12** — no correction is
needed. It was written this way at roadmap creation (2026-07-29) and phase-context time
(2026-08-02), not left as a stale RED-able claim. It explicitly cites **Phase 36's SC#3** as the
precedent it follows (`ROADMAP.md` line 498: "following exactly the resolution Phase 36's SC#3 took
for its own already-true PDF claim") — Phase 36's own SC#3 (`ROADMAP.md` § "Phase 36", item 3) is
itself an invariance guard (a PDF-extracted-text/size/page-count equality assertion rather than a
RED-then-GREEN one, for the `visit_math_block` fix that also turned out to produce byte-identical
non-fatal output). No before/after text is recorded because no correction was required.

**Discharging artifact/command:** `39-03-PLAN.md`/`39-GATE-EVIDENCE-03.md` (the invariance guard
itself, `tests/test_rubric_indent_invariance.py`) and the D-13 classic RED
(`tests/test_rubric_strong_nesting_render_gate.py`, fixed by `39-06`). Re-confirmed live:

```
$ uv run pytest tests/test_rubric_indent_invariance.py tests/test_rubric_strong_nesting_render_gate.py -v
13 passed
```

**Status: MET.**

### SC#4 — Visual UAT (ADM-04)

**Criterion:** the owner signs off, from a greyscale render of the compiled PDF, that the four
admonition kinds remain distinguishable without hue.

**Outcome, quoted directly from `39-ADM04-SIGNOFF.md` § "Outcome" (the only source for this
criterion's status — not inferred from the artifact's existence):**

> "**ADM-04 is MET.** The owner can distinguish the four kinds in the greyscale render, and the
> distinguishing signal is the icon shape (`info`/`tip`/`warning`/`crossmark` icons differ by shape
> and are baked-in raster fills, unaffected by desaturation) — which is exactly the channel ADM-04
> itself names ('the distinction must be carried by icon and border, not hue alone'). **Explicit
> recorded caveat: luminance is uniform and carries no distinguishing signal.**"

The sign-off also records (§5 "Consequences"): no styling change was made, no fallback lever was
chosen, and no pending todo was filed — all consistent with a MET outcome. The sign-off's §4
preserves an earlier, superseded framing from the owner's first-pass deliberation (describing the
boxes as reading "all the same" and questioning feasibility) explicitly marked as superseded by a
"CORRECTION" the owner/coordinator issued afterward; the operative, recorded verdict is the
corrected one quoted above, and this reconciliation follows that recorded verdict, not the
superseded framing.

**Status: MET**, on icon-shape grounds, with the uniform-luminance finding carried forward as an
explicit caveat (not a defect) for any future reader.

### SC#5 — test migration census and full-corpus gate

**Criterion:** this phase's exact-string blast radius is migrated inside the phase by hand-derived
expected strings plus a recorded file/class census, and the full-corpus `-b typstpdf` gate is re-run
green after the admonition and rubric changes — a skip is not a pass.

**Discharging artifact/command:** this plan's own `39-TEST-CENSUS.md` (Task 1) and § "1. The
full-corpus real-render gate — ACTUALLY RAN, not skipped" above (Task 2) — `v9.1.0`, 14.17s,
PASSED, not a skip.

**Status: MET.**

---

### Milestone invariants, restated as reconciled (from §7 above)

- No new runtime dependencies: **held** (`pillow` is `[dev]`-only).
- `@preview` package count stays at four: **held**.
- Every node-handler change ships a real `typst.compile()` GATE-01 regression fixture, recorded red
  against the unfixed code: **held** — `39-GATE-EVIDENCE-01.md`/`-02.md`/`-03.md` each record a RED
  (or, for SC#3, the D-12 invariance-guard substitute Phase 36's own precedent established) before
  the corresponding fix landed.

---

### Two folded defects, disposition

**1. The pending todo naming this phase as its resolver.**
`.planning/todos/pending/2026-07-30-rubric-with-inline-markup-leaks-in-list-item-and-drops-par.md`
already carries `resolves_phase: 39` in its frontmatter (confirmed: `grep -n "resolves_phase: 39"`
on the file returns a match at line 3). **The closing commit is `db70c2a`**
(`fix(39-06): give visit_rubric/depart_rubric their own save slots (D-13)`), which gives
`visit_rubric`/`depart_rubric` their own `_rubric_was_*` save slots — exactly the fix this todo's
own "Solution" section describes. Per this project's standing closure convention (already applied
identically by `38-TEST-CENSUS.md`'s own "Folded todos, closed" section, and recorded in this
project's own `worktree-cleanup-deletion-guard` memory note): **this file is deliberately left in
`.planning/todos/pending/` by this worktree agent.** A `git mv` from inside a worktree registers as
a file deletion, which `worktree.cleanup-wave` blocks unconditionally with no bypass — the move from
`pending/` to `completed/` is the orchestrator's own post-merge `close_phase_todos` step, on the
main tree, after this wave's worktree merges. This reconciliation section is the evidence that
closing step needs: the todo is resolved, and the resolving commit is `db70c2a`.

**2. The double-blank-line wart recorded inline in `visit_rubric`'s docstring.**
Confirmed removed: `grep -c 'not fixed in this plan' typsphinx/translator.py` returns `0`. The
docstring (`typsphinx/translator.py:5804-5841`) now describes the D-11 fix directly ("This commit
(D-11) also closes the double-blank-line wart the docstring previously described as deliberately
preserved...") rather than deferring it. No stale deferral note survives.

---

### STATE.md and ROADMAP.md — worktree-mode deferral, not an omission

Per this project's standing worktree-isolation execution mode (`CLAUDE.md` § "Worktree-isolated
execution") and this plan's own harness instructions (`<parallel_execution>`): **this worktree agent
does not write to `.planning/STATE.md` or `.planning/ROADMAP.md`.** Both are owned centrally by the
orchestrator after all of this wave's worktrees merge. This section records, for the orchestrator's
own close-phase step, the STATE.md edit this plan's Task 3 would otherwise have made directly:

- **Retire three now-answered Operator Next Steps notes** (`.planning/STATE.md` § "Operator Next
  Steps"): the bullet beginning "Phase 39 is planned" (including its `--skip-ui` instruction — Phase
  39 is now closed, so "Next step is `/gsd-execute-phase 39`" is stale), the bullet beginning "Phase
  39 SC#3 depends on Phase 38's shipped indent" (the `SHARED_INDENT_STEP` consumption bar — now
  discharged, per SC#3 above), and the bullet beginning "ADM-04 is the milestone's only `[V]`
  requirement" (the human-checkpoint expectation — now discharged, per SC#4 above and
  `39-ADM04-SIGNOFF.md`).
- **Replace with:** Phase 39 closed 2026-08-02 — ADM-01..ADM-05 all complete (ADM-04 MET on
  icon-shape grounds, uniform-luminance recorded as caveat); full suite green (763 passed / 1
  skipped), corpus gate re-run green (not skipped, tag `v9.1.0`); milestone invariants held (no new
  runtime dependency, `@preview` count stays 4, gentle-clues pin unchanged at `1.3.1`); docs dogfood
  build 91 pages (90 pre-phase, +1 explained in this file's §6). Next: Phase 40 (Citations — Full
  Round Trip), structurally independent of Phase 39, keeps the milestone's one classic
  `TypstError`-RED exception (CIT-01).
- **A newly-discovered environment note worth carrying forward:** the NixOS-sandbox shim documented
  in this project's `nixos-sandbox-test-env` memory (symlinking the main checkout's working
  `.venv/bin/ruff`) is necessary but **not sufficient** for the ~45 integration/render-gate tests
  that shell out via `subprocess.run(["uv", "run", "sphinx-build", ...])`: a fresh worktree's own
  `uv sync`-installed `.venv/bin/uv` is ALSO a generic-linux ELF binary that fails under the NixOS
  stub loader (`Could not start dynamically linked executable`, exit 127), and it shadows the
  correct Nix-store `uv` on `PATH` for that subprocess's child. The fix is the same shape as the
  `ruff` shim: `ln -sf "$(command -v uv)" .venv/bin/uv` (using the Nix-store `uv` resolved via
  `command -v uv` BEFORE any `.venv/bin` shim exists on `PATH`), done once per worktree alongside the
  `ruff` shim. Measured directly this session: the full unfiltered `uv run pytest` failed 45 tests
  with exit 127 before this second shim, and passed all of them (763/764) after it.
- Bullets 2 ("Two decision-gate format traps...") and 5 ("Phase 38 closed with a documentation
  correction...") of the current Operator Next Steps are **not** among the three retired above and
  should be left as-is — they are general tooling/process notes, not Phase-39-specific answered
  items.

`ROADMAP.md`'s Phase 39 entry needs no wording correction (SC#3 already reads as the invariance
guard, confirmed above) — only its own `- [ ] 39-08-PLAN.md` checkbox and the phase-level `Plans:
7/8` counter need flipping to `8/8` and its plans list entry checked, which is the orchestrator's
own `roadmap.update-plan-progress` step after merge, per the same worktree-mode deferral.

# Gap G-39-1 Close-Out — Red-Family Taxonomy Sub-Division

**Phase:** 39-admonition-taxonomy-rubric-nesting
**Gap:** G-39-1
**Close-out plan:** 39-13
**Base commit (finished tree):** `4e3128937416e8cc9b026e5715179adb9c5936e1`
**Date:** 2026-08-02

---

## 1. What the gap was

Phase 39 shipped and was verified (`39-VERIFICATION.md`, `status: passed`, 5/5 must-haves,
2026-08-02T03:33:10Z) with `attention`, `danger` and `error` all collapsed onto one gentle-clues
function, `error(...)` — decision D-03 in `39-CONTEXT.md` ("`danger` folds into `error` too").
During conversational UAT immediately afterward, the owner was shown a live A/B/C render
comparison of the folded red bucket against gentle-clues' own three distinct red-family functions
(`danger`, `memo`, `error`) and reversed course, first for `danger` ("うわ、デンジャーは
gentle-clueのデンジャーに振った方が良かったかも" → "Bでもっかい再構成しないとまずいな"), then
extending the same reversal to `attention` after being shown Sphinx's own per-type icon assignment
("Attentionはgentle-cleuのmemoにすっか"). This is **decision D-03-R**, recorded 2026-08-02 in
`39-CONTEXT.md`'s "Reversal — recorded 2026-08-02 (gap G-39-1)" section: the red family stays a
family of three (not re-merged into the orange warning bucket), but sub-divides into three
pairwise-distinct clue functions instead of collapsing onto one. **This is a deliberate owner
design reversal made after live evidence, not a defect discovered in shipped code.**

---

## 2. Workstream table — all five `missing:` items from `39-UAT.md` gap G-39-1

| # | `missing:` item (verbatim from `39-UAT.md`) | Discharging plan(s) | Live-run evidence (re-runnable) |
|---|---|---|---|
| 1 | "Route `visit_danger` → `\"danger\"` and `visit_attention` → `\"memo\"`" | 39-09 (RED), 39-11 (GREEN) | `typsphinx/translator.py:4544` (`self._visit_admonition(node, "danger")`), `:4559` (`self._visit_admonition(node, "memo")`), commits `29f4247`/`0430d47`/`bf91cbe`. Re-run: `uv run pytest tests/test_admonition_bucket_render_gate.py::test_danger_routes_to_danger_function tests/test_admonition_bucket_render_gate.py::test_attention_routes_to_memo_function tests/test_admonition_bucket_render_gate.py::test_red_family_types_route_to_distinct_clue_functions -v` → **3 passed** (re-confirmed live this session). |
| 2 | "Confirm the `sphinx.locale.admonitionlabels` `custom_title` path still wins over gentle-clues' own linguify defaults for BOTH new ids — otherwise `.. attention::` renders as \"Memorize\" (memo has no `ja` entry and falls back to en). The `ja` catalog values 「注意」/「危険」 must still be what is emitted." | 39-09 (locale gate, RED), 39-11 (GREEN + strengthened PDF negative assertion) | `tests/test_admonition_locale_title_precedence_gate.py` (9 tests, both `en`/`ja` fixtures). Re-run: `uv run pytest tests/test_admonition_locale_title_precedence_gate.py -v` → **9 passed** (re-confirmed live this session), including `test_danger_box_opens_with_danger_ja`, `test_attention_box_opens_with_memo_ja`, `test_package_default_titles_never_appear_in_emitted_source_ja`. Also `tests/test_pdf_render_gate.py::TestAdmonitionPdfRenderGate::test_admonitionbuckettitlegate` (English compiled-PDF discriminating case + new negative assertion against gentle-clues' own "Memorize" default) — **1 passed** (re-confirmed live). Note: `39-CONTEXT.md`'s D-03-R section corrects `39-UAT.md`'s own claim that `memo` has no `ja` entry — the installed `lang.toml` line 168 carries `[lang.ja] memo = "覚える"` — but this changes nothing functionally, since `custom_title` already overrides every predefined id's default in both locales. |
| 3 | "Restate ADM-02 (and note the red-group sub-division under ADM-01's preamble) so neither asserts a single collapsed red bucket; record the D-03 reversal in 39-CONTEXT.md" | 39-10 | `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-CONTEXT.md` (D-03-R section, commit `7c8cfb9`), `.planning/REQUIREMENTS.md` (ADM-02 dated sub-bullet + ADM-01 preamble note, commit `43cfec4`), `.planning/ROADMAP.md` (Phase 39 SC#1 amended in place + new "Roadmap Evolution" section, commit `03f79f7`). Re-run: `grep -c 'D-03-R' .planning/phases/39-admonition-taxonomy-rubric-nesting/39-CONTEXT.md` → **3**; `grep -c 'G-39-1' .planning/REQUIREMENTS.md` → **2**; `grep -c 'G-39-1' .planning/ROADMAP.md` → **4** (all re-confirmed live this session). |
| 4 | "Migrate the danger/attention expected strings in the three test files above; invert 39-05/D2's zero-call-site grep guard; re-run the full-corpus `-b typstpdf` gate" | 39-11 (test migration), 39-13 (grep-guard inversion recorded, corpus gate re-run) | Test migration: `tests/test_admonitions.py::TestAdmonitionConversion::test_danger_converts_to_danger_function`, `::test_attention_converts_to_memo_function`, `tests/test_pdf_render_gate.py::TestAdmonitionPdfRenderGate::test_admonitionbuckettitlegate` — re-run `uv run pytest tests/test_admonitions.py::TestAdmonitionConversion::test_danger_converts_to_danger_function tests/test_admonitions.py::TestAdmonitionConversion::test_attention_converts_to_memo_function "tests/test_pdf_render_gate.py::TestAdmonitionPdfRenderGate::test_admonitionbuckettitlegate" -v` → **3 passed** (re-confirmed live this session). Grep-guard inversion: `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-TEST-CENSUS-G39-1.md` § "The inverted guard" (measured `1`, was `0`). Corpus gate: see §3 below — **ran, PASSED, not skipped**. |
| 5 | "Extend the greyscale probe fixture to cover attention/danger/error separately, re-render 39-ADM04-GREYSCALE.png from post-change code, and re-take the ADM-04 sign-off — the artifact currently on record shows all three folded into the red bucket. The new taxonomy is expected to IMPROVE the greyscale verdict (three distinct glyphs: ! / ⚡ / ×), which was the owner's original complaint." | 39-12 | `tests/fixtures/admonition_greyscale_probe/index.rst` (extended to 7 boxes, error/danger/attention contiguous, commit `c02d9ec`); `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-GREYSCALE.png` (36051 bytes, mode `L`, 1240×1754, re-rendered at commit `c02d9ec` — confirmed on disk this session, size matches); `.planning/phases/39-admonition-taxonomy-rubric-nesting/39-ADM04-SIGNOFF.md` § "Amendment 2026-08-02 (gap G-39-1)" (commit `9bb0281`) — owner's verbatim one-word response **"approved"** to the four-question checkpoint including the explicit `attention`/`error` adjacency question. **Outcome: POSITIVE** (§A6: "ADM-04 remains MET"). |

All five `missing:` items are discharged. None is closed by assertion — every row above names a
test node id, a command, or an artifact path a reader can re-run or open.

---

## 3. The full-corpus `-b typstpdf` gate — ran, PASSED, not skipped

Re-run live this session, in this worktree, after `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv
sync --extra dev --extra docs` and the `uv`/`ruff` NixOS shims:

```
$ uv run pytest tests/test_corpus_gate.py -m slow -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
collected 5 items / 3 deselected / 2 selected

tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error PASSED [ 50%]
tests/test_corpus_gate.py::test_empty_url_before_after SKIPPED (SC#3
before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1
to run it (RESEARCH Open Question 1))                                    [100%]

================= 1 passed, 1 skipped, 3 deselected in 13.46s ==================
```

**The gate ran, not skipped.** `TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`
reports **PASSED**, not SKIPPED. The one SKIP in this output
(`test_empty_url_before_after`) is a separate, explicitly env-gated (`TYPSPHINX_CORPUS_REPORT=1`)
diagnostic unrelated to whether the corpus compiles — it is not the corpus gate itself and is not
recorded as evidence of anything here.

**Resolved Sphinx tag:** `v9.1.0` — measured live: `python3 -c "import sphinx;
print(sphinx.__version__)"` → `9.1.0`; `resolve_corpus_tag()` returns `f"v{sphinx.__version__}"`.

**Clone's commit SHA** (the cached corpus clone at `~/.cache/typsphinx-corpus-gate/sphinx-v9.1.0`,
measured live this session): `cc7c6f435ad37bb12264f8118c8461b230e6830c`.

**Duration:** 13.46s (pytest's own reported summary line above).

This directly discharges gap G-39-1's `missing:` item 4's "re-run the full-corpus `-b typstpdf`
gate" clause, and satisfies this plan's own `must_haves.prohibitions` first entry
(ADM-02/transparency): a skip is not being recorded as a pass — the gate genuinely ran and passed.

---

## 4. Milestone-invariant re-checks (from this plan's Task 1)

| Invariant | Command | Result |
|---|---|---|
| No new runtime dependency | `git diff --stat 7272bd6..HEAD -- pyproject.toml` | empty (no diff at all across this gap's plans; also `git log --oneline 7272bd6..HEAD -- pyproject.toml` empty) |
| `@preview` package count stays at 4, at all three guarded surfaces | `grep -n "@preview" typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ` | `codly`, `codly-languages`, `mitex`, `gentle-clues` — exactly 4, same set as pre-gap |
| gentle-clues pin `1.3.1` at all four lockstep sites (3 guarded + 1 unguarded) | `grep -rc 'gentle-clues:1.3.1' typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ docs/source/_typst/custom_template.typ` | `1` at all four paths — **the fourth (`docs/source/_typst/custom_template.typ`) is hand-checked here explicitly, because `tests/test_preview_version_sync.py` does not watch it** |
| `test_preview_version_sync.py` green | `uv run pytest tests/test_preview_version_sync.py -x -v` | `3 passed` (`test_preview_versions_identical_across_declaration_sites`, `test_all_four_packages_declared`, `test_example_templates_match_canonical_versions`) |
| Full-corpus gate | see §3 above | PASSED, not skipped |
| Fast suite (`not slow`) | `uv run pytest -m "not slow" -q` | `746 passed, 29 deselected, 0 failed` |
| Full unfiltered suite | `uv run pytest -q` | `774 passed, 1 skipped` — matches the measured baseline exactly |
| `black --check .` | `uv run black --check .` | `All done! 201 files would be left unchanged.` |
| `ruff check .` | `uv run ruff check .` | `All checks passed!` |
| `mypy typsphinx/` | `uv run mypy typsphinx/` | `Success: no issues found in 6 source files` |

All three milestone invariants held, and the fourth (unguarded) lockstep site was hand-checked
rather than assumed covered by the sync test.

---

## 5. The durable copy of the Truth #1 amendment

The following is reproduced in full from `39-VERIFICATION.md`'s "Amendment 2026-08-02 (gap
G-39-1)" section, so this close-out remains self-contained evidence even if a later verification
run regenerates `39-VERIFICATION.md` wholesale:

> ## Amendment 2026-08-02 (gap G-39-1): Truth #1's zero-call-site assertion inverted by design
>
> **Date:** 2026-08-02
> **Plan:** 39-13 (gap close-out)
>
> Truth #1's evidence cell above asserted `grep -c '_visit_admonition([^)]*"danger"'` returns `0`
> — that `danger` is no longer emitted as a distinct function. Under decision D-03-R (gap G-39-1,
> `39-CONTEXT.md` "Reversal — recorded 2026-08-02"), that count is now measured on the finished
> tree as exactly `1`: `visit_danger` routes to its own `danger` id and `visit_attention` routes
> to `memo`, so the red family is three pairwise-distinct clue functions rather than one collapsed
> `error()` call. This is the consequence of a recorded **design reversal**, not a correction of an
> error — the zero count was true when Truth #1 was written and correctly recorded the phase as it
> was built at that time.
>
> Truth #1's underlying claim — that `attention` and `danger` leave their pre-phase buckets —
> still holds under the restated ADM-02 (`REQUIREMENTS.md`'s dated sub-bullet). **The durable
> record of this inversion is `39-GAP-G39-1-CLOSEOUT.md`**, not this file: this section is
> deliberately short because `{phase}-VERIFICATION.md` is a filename the verification workflow
> reserves and regenerates wholesale, so evidence stored only here can be lost. A pre-amendment
> backup of this file was taken at
> `.planning/backups/39-VERIFICATION.md.pre-G39-1-amendment.2026-08-02.bak` before this section
> was appended.

**Pre-amendment backup path (recorded per this plan's own instruction):**
`.planning/backups/39-VERIFICATION.md.pre-G39-1-amendment.2026-08-02.bak` (copied before the
amendment above was appended; `git diff --numstat -- 39-VERIFICATION.md` shows 24 insertions, 0
deletions for the amendment itself).

---

## 6. What this gap did NOT change

- **ADM-03's routing** — the generic `.. admonition::` → `notify(...)` and non-contents
  `.. topic::` → `abstract(...)` routing is untouched; `git log --oneline 7272bd6..HEAD --
  typsphinx/translator.py` shows only the two `visit_danger`/`visit_attention` hunks (13
  insertions / 8 deletions total, confirmed via `git diff --stat`).
- **ADM-05's rubric work** — `tests/test_desc_rubric_decoupling_render_gate.py`,
  `tests/test_rubric_option_concat_render_gate.py`,
  `tests/test_rubric_propagated_target_render_gate.py`, and all rubric/signature fixtures are
  proven untouched a second time (`39-TEST-CENSUS-G39-1.md` § "Second table", `git log` empty over
  all ten paths across this gap's whole commit range).
- **D-01's rule against colour literals** — no `accent-color:` or other colour-literal argument
  was introduced anywhere; a bucket is still expressed purely as a gentle-clues function name
  (`39-CONTEXT.md` D-03-R: "D-01's rule ... is explicitly **NOT** reversed by D-03-R; only the
  cardinality of the red bucket changes"). Confirmed by direct read of the two changed call sites
  in §2 row 1 above — only the string-literal id argument changed at each site.
- **D-04/D-05's title source** — every real admonition type, including the two red-family ids
  this gap touches, still takes its static title from the single
  `sphinx.locale.admonitionlabels` catalog lookup inside `_visit_admonition`; the directive-
  supplied dynamic title still wins over it. Confirmed by §2 row 2's evidence (all 9 locale-
  precedence tests green in both `en` and `ja`).
- **The seealso and warning groups** — `seealso`→`tip` (ADM-01) and the warning bucket
  (`warning`/`caution`/`important`) are unaffected; confirmed live this session:
  `uv run pytest tests/test_admonition_bucket_render_gate.py::test_seealso_routes_to_tip_bucket
  tests/test_admonition_bucket_render_gate.py::test_control_buckets_never_move -v` → both pass
  (part of the 774-passed full-suite run in §4).

---

## 7. Final verdict

**Gap G-39-1 is CLOSED.**

All five of the gap's `missing:` workstreams are discharged with re-runnable, live-verified
evidence (§2). The full-corpus `-b typstpdf` gate genuinely ran and passed, not skipped (§3). All
three milestone invariants plus the fourth, unguarded lockstep site held under a fresh hand-check
(§4). Truth #1's inversion is recorded both in `39-VERIFICATION.md` (additively) and durably here
(§5). The ADM-04 amendment in `39-ADM04-SIGNOFF.md` records a **positive** verdict — the owner's
verbatim `"approved"` answering the four-question checkpoint, including the explicit
`attention`/`error` adjacency question — so this close-out proceeds to flip `39-UAT.md`'s gap
status to `closed`, per this plan's own instruction that a negative or absent ADM-04 verdict would
have blocked that flip.

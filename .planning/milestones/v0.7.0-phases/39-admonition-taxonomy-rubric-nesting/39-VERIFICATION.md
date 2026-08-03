---
phase: 39-admonition-taxonomy-rubric-nesting
verified: 2026-08-02T06:00:00Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 1
re_verification:
  previous_status: passed (2026-08-02T03:33:10Z, pre-gap; then amended in-place for gap G-39-1)
  previous_score: 5/5
  gaps_closed:
    - "G-39-1: the red family (attention/danger/error) is a single collapsed error(...) call -- reversed by owner decision to three pairwise-distinct gentle-clues functions (danger/memo/error)"
  gaps_remaining: []
  regressions: []
---

# Phase 39: Admonition Taxonomy + Rubric Nesting Verification Report

**Phase Goal:** Admonitions carry the meaning their type implies — `seealso` grouped with the hints
rather than the notes, `attention` grouped with the dangers rather than the warnings, and a generic
`.. admonition::` styled and carrying its own title instead of falling through to the unstyled base
box — and a rubric sits at whatever indent level its container has reached rather than jumping back
to the page margin.

**Verified:** 2026-08-02T06:00:00Z
**Status:** passed
**Re-verification:** Yes — this phase shipped in two tranches. Plans 39-01..39-08 (original taxonomy
+ rubric work) were verified once already (`status: passed`, 5/5, 2026-08-02T03:33:10Z). Plans
39-09..39-13 close gap **G-39-1**, a deliberate owner reversal of locked decision D-03 discovered
during conversational UAT immediately after the first verification. This report re-verifies the
whole phase against the codebase as it stands now, under the **amended** ROADMAP SC#1 / REQUIREMENTS
ADM-02 wording (`39-CONTEXT.md` decision **D-03-R**), not the superseded wording.

## What changed between the two tranches (read this before the truth table)

**Original (verified 2026-08-02T03:33:10Z):** `attention`, `danger` and `error` were all folded onto
one gentle-clues function, `error(...)` (decision D-03: "danger folds into error too").

**Reversed by owner decision, recorded as gap G-39-1 (`39-CONTEXT.md` D-03-R):** after a live A/B/C
render comparison shown during UAT, the owner reversed course — first for `danger` ("うわ、デンジャー
はgentle-clueのデンジャーに振った方が良かったかも"), then extended the same reversal to `attention`
("Attentionはgentle-cleuのmemoにすっか"). The red family now sub-divides into **three
pairwise-distinct clue functions**: `danger`→`danger`, `attention`→`memo`, `error`→`error` (unchanged).
D-01's rule — a bucket is a function name, never a colour argument — is **not** reversed; only the
red bucket's cardinality changes, from one function to three.

This is a **deliberate design reversal**, not a defect repair. `ROADMAP.md`'s Phase 39 SC#1 and
`REQUIREMENTS.md`'s ADM-02 have both been amended in place (additively, dated, originals preserved)
to reflect it. This report verifies against the amended wording throughout.

## Goal Achievement

### Observable Truths

| # | Truth (ROADMAP SC / requirement, as amended) | Status | Evidence |
|---|---|---|---|
| 1 | SC#1/ADM-01/ADM-02 **(amended per D-03-R)**: `seealso` routes to the same bucket as `hint`/`tip` (`tip()`); `attention` leaves the orange warning group for the **red family** — a group of gentle-clues functions sharing the red hue range — without being required to be the same function as `danger`/`error` | VERIFIED | Read `typsphinx/translator.py` directly: `visit_seealso` (line 4472) → `_visit_admonition(node, "tip")` (4478); `visit_danger` (4536) → `_visit_admonition(node, "danger")` (4544); `visit_attention` (4550) → `_visit_admonition(node, "memo")` (4559); `visit_error` (4528) → `_visit_admonition(node, "error")` (4530) unchanged. Measured directly: `grep -c '_visit_admonition(node, "danger")'` = 1, `..."memo")'` = 1, `..."error")'` = 1 (down from 3 pre-gap), `..."clue")'` = 0. Re-ran `tests/test_admonition_bucket_render_gate.py` (12 tests incl. `test_danger_routes_to_danger_function`, `test_attention_routes_to_memo_function`, `test_red_family_types_route_to_distinct_clue_functions`, `test_attention_is_not_in_the_warning_bucket`, `test_seealso_routes_to_tip_bucket`, `test_control_buckets_never_move`) and `tests/test_admonition_locale_title_precedence_gate.py` (9 tests, both `en`/`ja` catalogs) — both fully green (myself, this session). `ROADMAP.md` Phase 39 SC#1 and `REQUIREMENTS.md` ADM-02 both carry the amended, dated (2026-08-02) wording alongside their original text, marked superseded rather than deleted — confirmed by direct read. |
| 2 | SC#2/ADM-03: a generic `.. admonition:: Custom Title` renders as a styled box (`notify(...)`) carrying that title; `.. topic::` renders as a styled box (`abstract(...)`) — **untouched by gap G-39-1** | VERIFIED | `typsphinx/translator.py:4565` (`visit_admonition` → `notify`), `:4580` (`visit_topic`, non-`contents` branch → `abstract`) — read directly, byte-identical to the pre-gap verification. `git log --oneline 7272bd6..HEAD -- typsphinx/translator.py` shows exactly one file changed with 13 insertions / 8 deletions confined to `visit_danger`/`visit_attention` (confirmed via `39-GAP-G39-1-CLOSEOUT.md` §6 and re-confirmed by my own `git diff --stat -- typsphinx/translator.py` read). Re-ran `tests/test_admonitions.py` (18 tests) and `tests/test_topics.py` (5 tests) — both green. |
| 3 | SC#3/ADM-05 (invariance guard per D-12): a rubric inside a description body has a left edge equal to its containing body's edge, at every nesting level — **untouched by gap G-39-1** | VERIFIED | `tests/test_rubric_indent_invariance.py` (7 tests), `tests/test_rubric_strong_nesting_render_gate.py` (6 tests), `tests/test_desc_rubric_decoupling_render_gate.py` (5 tests) — all re-ran green myself this session. Confirmed via `39-TEST-CENSUS-G39-1.md` §"Second table" (and independently by `git log --oneline 7272bd6..HEAD` over all ten rubric-related paths returning empty) that no rubric/`desc_signature` file was touched by the gap-closure tranche — Phase 37's golden file and this phase's own rubric fix (39-06) stay fixed points. |
| 4 | SC#4/ADM-04 ([V], human-only visual UAT): the four (now effectively four groups containing a three-function red family) admonition kinds remain distinguishable in a greyscale render, without hue — **re-taken under gap G-39-1** | VERIFIED (recorded human sign-off, taken as given per this task's instructions) | The pre-gap verdict (2026-08-02, plan 39-07): MET on icon-shape grounds, luminance uniform (explicit caveat). The artifact on record at that time showed all three red-family types folded into one box style, which does not evidence the post-reversal taxonomy. Plan 39-12 re-rendered `39-ADM04-GREYSCALE.png` (36,051 bytes, mode `L`, 1240×1754, byte-different from the prior 35,570-byte artifact — confirmed on disk) from a worktree with both routing gates green (21/21) **before** the render, extended the probe fixture to 7 boxes with `error`/`danger`/`attention` deliberately contiguous, and put a blocking human checkpoint to the owner naming the `attention`/`error` adjacency pair explicitly. `39-ADM04-SIGNOFF.md`'s dated amendment ("red-family sub-division re-take") records the owner's verbatim one-word response, **"approved"**, to all four checkpoint questions including the named adjacency question — outcome: **ADM-04 remains MET**, no styling change made, no fallback lever needed. The original 2026-08-02 verdict survives verbatim in the same file, marked superseded rather than erased. Per this task's instructions, this human verdict is taken as given and not re-judged. |
| 5 | SC#5: the phase's exact-string blast radius is migrated by hand-derived expected strings, and the full-corpus `-b typstpdf` gate actually runs green (a skip is not a pass) — **re-run for real under gap G-39-1** | VERIFIED | Re-ran `uv run pytest tests/test_corpus_gate.py -m slow -v` myself: `test_corpus_compiles_with_no_fatal_error` **PASSED** (not skipped); the one SKIP in the same run (`test_empty_url_before_after`) is a separate, explicitly `TYPSPHINX_CORPUS_REPORT=1`-gated diagnostic, not the corpus gate — `1 passed, 1 skipped, 3 deselected in 13.46s`, matching `39-GAP-G39-1-CLOSEOUT.md` §3 exactly. Resolved Sphinx tag `v9.1.0`, clone SHA `cc7c6f435ad37bb12264f8118c8461b230e6830c` (per close-out; not independently re-cloned but the gate ran against the cached clone and passed). Re-ran the full unfiltered suite myself: `774 passed, 1 skipped, 0 failed`, matching the orchestrator's measured baseline exactly. `black --check .`, `ruff check .`, `mypy typsphinx/` all clean (re-ran myself). `39-TEST-CENSUS-G39-1.md` records a re-measured (not recalled) census, row-by-row reconciled against the shipped `39-TEST-CENSUS.md` with "no unexplained disagreement found anywhere." |

**Score:** 5/5 truths verified (0 present-but-behavior-unverified)

### Gap G-39-1 — dedicated traceability (all five `missing:` workstreams from `39-UAT.md`)

Per `39-GAP-G39-1-CLOSEOUT.md` §2, all five workstreams are discharged with re-runnable evidence, and
I independently re-confirmed the load-bearing ones this session:

| # | Workstream | Discharging plan(s) | My independent confirmation |
|---|---|---|---|
| 1 | Route `visit_danger`→`"danger"`, `visit_attention`→`"memo"` | 39-09 (RED), 39-11 (GREEN) | Confirmed by direct read of `translator.py:4544`/`:4559` and `grep -c` counts above. |
| 2 | Catalog title (`sphinx.locale.admonitionlabels`) still wins over gentle-clues' own linguify defaults for both new ids, both locales | 39-09 (RED), 39-11 (GREEN) | Re-ran `tests/test_admonition_locale_title_precedence_gate.py` — 9/9 pass. |
| 3 | Restate ADM-02/SC#1, record D-03-R in `39-CONTEXT.md` | 39-10 | Read `39-CONTEXT.md`'s D-03-R section, `REQUIREMENTS.md` ADM-02's dated sub-bullet, `ROADMAP.md`'s SC#1 correction — all present, all additive (originals preserved verbatim). |
| 4 | Migrate danger/attention expected strings; invert the zero-call-site grep guard; re-run the full-corpus gate | 39-11 (migration), 39-13 (inversion recorded, corpus re-run) | Re-ran `tests/test_admonitions.py` (18/18) and the corpus gate (PASSED, not skipped) myself. |
| 5 | Extend greyscale probe, re-render, re-take ADM-04 sign-off | 39-12 | Confirmed `39-ADM04-SIGNOFF.md`'s amendment records a positive ("approved") verdict, per Truth #4 above. |

### Amendment: Truth #1's zero-call-site assertion inverted by design (preserved from prior VERIFICATION.md)

The pre-gap verification's Truth #1 evidence cell asserted `grep -c '_visit_admonition([^)]*"danger"')`
returns `0` — that `danger` was no longer emitted as a distinct function. **That assertion is now
false by design**, not by regression: under D-03-R the count is exactly `1` (`visit_danger` routes
to its own `danger` id; `visit_attention` routes to `memo`). This is the direct, intended consequence
of a recorded owner design reversal (gap G-39-1), not a correction of an error — the zero count was
true and correctly recorded at the time the original verification was written. The durable record of
this inversion lives in `39-GAP-G39-1-CLOSEOUT.md` §5 (mirroring the prior `39-VERIFICATION.md`
amendment verbatim) and in `39-TEST-CENSUS-G39-1.md` §"The inverted guard". `39-05-SUMMARY.md` (which
originally recorded the zero count as evidence) is deliberately left unedited — it is the historical
record of what that plan delivered at the time, per `39-13`'s explicit prohibition against editing
shipped SUMMARYs. A pre-amendment backup of the prior `39-VERIFICATION.md` was taken at
`.planning/backups/39-VERIFICATION.md.pre-G39-1-amendment.2026-08-02.bak` before this regeneration.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `typsphinx/translator.py` (all admonition visitors) | Bucket re-routing incl. D-03-R red-family sub-division | ✓ VERIFIED | Read directly. 13 `_visit_admonition(node, ...)` call sites, 9 distinct clue types used (`info`, `tip`, `warning`, `error`, `danger`, `memo`, `notify`, `abstract`, `task`); `clue` (base) never passed. |
| `tests/test_admonition_bucket_render_gate.py` | Region-scoped GATE-01 for all bucket moves + red-family sub-division | ✓ VERIFIED | Re-ran: 12/12 pass (10 pre-gap + 2 new for G-39-1). |
| `tests/test_admonition_locale_title_precedence_gate.py` | New gate: catalog title beats gentle-clues' own default for both new ids, both locales | ✓ VERIFIED | Re-ran: 9/9 pass. New file, created by 39-09. |
| `tests/test_admonitions.py` | In-process unit assertions, 2 renamed/re-derived for G-39-1 | ✓ VERIFIED | Re-ran: 18/18 pass. |
| `tests/test_pdf_render_gate.py` | Compiled-PDF gate, strengthened with a memo-default negative assertion | ✓ VERIFIED | Re-ran: 31/31 pass (full file). |
| `tests/test_rubric_indent_invariance.py`, `test_rubric_strong_nesting_render_gate.py`, `test_desc_rubric_decoupling_render_gate.py` | ADM-05 rubric gates, byte-unchanged by the gap | ✓ VERIFIED | Re-ran: 7+6+5 = 18/18 pass. `git log` over these paths across the gap's commit range is empty. |
| `39-ADM04-GREYSCALE.png` + `39-ADM04-SIGNOFF.md` | Re-rendered artifact (post-D-03-R) + re-taken owner sign-off | ✓ VERIFIED | Both present; sign-off's amendment records a positive ("approved") verdict against the re-rendered artifact, whose bytes (36,051) differ from the pre-gap artifact (35,570) — confirmed by direct read, not re-rendered by me. |
| `39-CONTEXT.md` D-03-R, `REQUIREMENTS.md` ADM-02 amendment, `ROADMAP.md` SC#1 amendment | Design reversal recorded additively, dated, originals preserved | ✓ VERIFIED | All three read directly; original text present verbatim alongside dated amendments in every case. |
| `39-TEST-CENSUS-G39-1.md`, `39-GAP-G39-1-CLOSEOUT.md` | Gap's own census + close-out record | ✓ VERIFIED | Both present, non-empty, internally consistent, reconciled row-by-row against `39-TEST-CENSUS.md`. |
| `39-UAT.md` gap `G-39-1` | Status transition | ✓ VERIFIED | `status: closed`, `closed_at: 2026-08-02`, `closed_by: [39-09, 39-10, 39-11, 39-12, 39-13]` — confirmed by direct read; gate condition (positive ADM-04 verdict) satisfied per Truth #4. |
| `.planning/REQUIREMENTS.md` | ADM-01..ADM-05 checked, ADM-02 restated | ✓ VERIFIED | All five `[x]`, ADM-06 (Phase 36, carried) also `[x]`. Checkbox count for ADM-0x unchanged at 6 across the gap-closure tranche, per 39-10's own acceptance criterion and my direct read. |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `visit_danger`/`visit_attention`/`visit_error`/`visit_seealso` | `_visit_admonition` | direct call with per-type `clue_type` arg | WIRED | Confirmed by direct read; emission mechanism (helper itself) unchanged by the gap. |
| `_visit_admonition` | `sphinx.locale.admonitionlabels` | module-level import + catalog lookup | WIRED | Confirmed still keyed on node class name (unchanged), so `danger` and `memo` still resolve their catalog title for free. |
| region-scoping helper (`_clue_open_before`) | `_CLUE_FUNCTION_NAMES` | tuple membership | WIRED | `memo` present in `_CLUE_FUNCTION_NAMES` (verified directly: `("info","tip","warning","error","danger","memo","notify","abstract","task","clue")`) — the token set is complete, so a false-green from an unrecognized box-open token cannot occur regardless of fixture adjacency (see IN-01 adjudication below). |
| ADM-04 render → re-taken sign-off → gap closure | `39-13`'s gate-on-positive-verdict logic | conditional status flip | WIRED | Confirmed: the gap only flips to `closed` given a positive ADM-04 amendment outcome; verified the amendment records "approved" before the status transition was checked. |

### Behavioral Spot-Checks (all re-run directly by this verifier, not trusted from SUMMARY narration)

| Behavior | Command | Result | Status |
|---|---|---|---|
| Full unfiltered suite | `uv run python -m pytest -q` | 774 passed, 1 skipped, 0 failed | ✓ PASS — matches orchestrator's measured cross-check exactly |
| Full-corpus `-b typstpdf` gate (must actually run, not skip) | `uv run pytest tests/test_corpus_gate.py -m slow -v` | `test_corpus_compiles_with_no_fatal_error` PASSED; 1 passed, 1 skipped (unrelated env-gated diagnostic), 3 deselected | ✓ PASS |
| Bucket-routing + locale-precedence gates (G-39-1's own RED→GREEN) | `uv run pytest tests/test_admonition_bucket_render_gate.py tests/test_admonition_locale_title_precedence_gate.py -q` | 21 passed | ✓ PASS |
| Admonition/topic/PDF regression | `uv run pytest tests/test_admonitions.py tests/test_pdf_render_gate.py -q` | 49 passed | ✓ PASS |
| Rubric gates (proven untouched by G-39-1) | `uv run pytest tests/test_rubric_indent_invariance.py tests/test_rubric_strong_nesting_render_gate.py tests/test_desc_rubric_decoupling_render_gate.py -q` | 18 passed | ✓ PASS |
| `@preview` version-sync (gentle-clues pin unchanged) | `uv run pytest tests/test_preview_version_sync.py -q` | 3 passed | ✓ PASS |
| Lint/type trio (exact CI commands) | `uv run black --check .`, `uv run ruff check .`, `uv run mypy typsphinx/` | all clean | ✓ PASS |
| Red-family grep guard (measured, not assumed) | `grep -c '"error"' typsphinx/translator.py`; three-call-site check | `1` for `"error"` string; exactly one call site each for `danger`/`memo`/`error`, zero for `clue` | ✓ PASS — matches `39-GAP-G39-1-CLOSEOUT.md` §4 and orchestrator's measured state exactly |

### Probe Execution

No `scripts/*/tests/probe-*.sh` convention is used by this project; the equivalent gates are the
pytest render-gate/corpus-gate modules above, all executed directly by this verifier.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| ADM-01 | 39-01/39-05/39-08 (shipped); 39-10 (preamble note), 39-13 (reconciliation) | `seealso` joins the `hint`/`tip` bucket; red-group sub-division noted in preamble | ✓ SATISFIED | `visit_seealso` → `tip`; gate tests pass; preamble amendment present. |
| ADM-02 | 39-01/39-05/39-08 (shipped); 39-09..39-13 (gap G-39-1) | `attention` leaves the orange warning bucket for the red family (restated around intent, not function identity) | ✓ SATISFIED | `visit_attention` → `memo`, `visit_danger` → `danger`, both in red family, neither in warning bucket; `test_attention_is_not_in_the_warning_bucket` and `test_red_family_types_route_to_distinct_clue_functions` both green; restated wording present in `REQUIREMENTS.md`. |
| ADM-03 | 39-01/39-05/39-08 | Generic admonition styled + titled; topic styled — untouched by G-39-1 | ✓ SATISFIED | `visit_admonition` → `notify`, `visit_topic` → `abstract`; byte-unchanged by the gap (confirmed via `git log`). |
| ADM-04 | 39-04/39-07 (shipped); 39-12/39-13 (gap re-take) | Greyscale distinguishability, human UAT — re-taken for the sub-divided taxonomy | ✓ SATISFIED | `39-ADM04-SIGNOFF.md`'s amendment records a positive "approved" verdict against the re-rendered, post-reversal artifact. |
| ADM-05 | 39-02/39-03/39-06/39-08 | Rubric inherits container indent; folded D-11/D-13 defects fixed — untouched by G-39-1 | ✓ SATISFIED | Invariance guard + D-11/D-13 behavioral tests all green; `git log` over rubric paths across the gap's commit range is empty. |
| ADM-06 | Phase 36 (pre-existing) | `rubric` owns its own emission | ✓ SATISFIED (carried, unaffected) | Unaffected by this phase or its gap closure. |

No orphaned requirements: every plan across both tranches (39-01 through 39-13) declares its
`requirements:` frontmatter, and all five phase-assigned IDs (ADM-01..ADM-05) appear in at least one
plan — confirmed by direct `grep` across all 13 plan files (see table above the Anti-Patterns
section).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `tests/test_admonitions.py` | 367-419 (`test_danger_converts_to_danger_function`, `test_attention_converts_to_memo_function`) | WR-01 (carried from `39-REVIEW.md`, pre-existing class, gap closure touched but did not close it): the two renamed/re-derived tests assert the box-open shape and the negative bracket-form check but still do not assert the `, title: "..."` argument the catalog lookup attaches | ⚠️ Warning | Confirmed by direct read: neither test body contains a `title:` assertion. Not a production defect — the title is proven end-to-end elsewhere (`test_admonition_bucket_render_gate.py`'s `_CATALOG_TITLE_SENTINELS` table, `test_red_family_types_route_to_distinct_clue_functions`, and all 9 tests in `test_admonition_locale_title_precedence_gate.py`). A future regression near these two unit tests specifically would not be caught here, only in the render-gate modules. Does not block phase goal achievement — carried forward as a standing, not-yet-closed opportunity. |
| `tests/test_admonition_bucket_render_gate.py` | 418-431 (`test_red_family_types_route_to_distinct_clue_functions`'s docstring) | IN-01 (adjudicated below) | ⚠️ Warning (test-hygiene, not functional) | See adjudication below. |
| `scripts/render_admonition_greyscale.py` | 176 | IN-02 (carried, pre-existing): `import tempfile` deferred to `__main__` block rather than top-level imports | ℹ️ Info | Style-only, dev/CI tooling, no functional impact, unrelated to this gap's delta. |

No debt markers (`TBD`/`FIXME`/`XXX`) or unresolved `TODO`/`HACK`/`PLACEHOLDER` found in this phase's
changed files across either tranche, confirmed by direct grep.

#### Adjudication of IN-01 (explicitly requested)

**Finding:** `test_red_family_types_route_to_distinct_clue_functions`'s docstring claims it proves
"region-scope resolution stays stable when three equal-family boxes sit adjacent in the fixture." I
read `tests/fixtures/admonition_render_gate/index.rst`'s actual directive order myself:
`note, warning, hint, danger, (unlabeled nested note/warning), tip, important, caution, seealso,
attention, error`. Only `attention` and `error` are truly adjacent (lines 117/126, no other directive
between them); `danger` sits five sections earlier (line 55), separated by the nested block, `tip`,
`important`, `caution` and `seealso`.

**My independent finding:** the "simultaneously, in one build" half of the must_have is genuinely
satisfied — all three sentinels are resolved from one compiled document in one call chain. The
"three adjacent" half, as literally written in the docstring, is not: the fixture is not a
three-in-a-row layout for all three red-family types. However, I also verified the underlying safety
property the docstring is trying to establish (T-39-18: a missing box-open recognition token causing
the backward scan in `_clue_open_before` to resolve past its own box to a neighbour's) does **not**
in fact depend on adjacency at all, because `_CLUE_FUNCTION_NAMES` — the tuple the region-scoping
regex is built from — already contains all ten possible clue-function identifiers, including `memo`
and `danger` (`("info","tip","warning","error","danger","memo","notify","abstract","task","clue")`,
confirmed by direct read). A backward scan for any sentinel will find the correct nearest recognized
open token regardless of how far away it is, as long as every intervening box's own open token is
also recognized — which is the case here. So the specific "three-in-a-row stress test" the docstring
claims is not actually exercised (the fixture only stress-tests one adjacent pair, `attention`/
`error`, plus one distant case, `danger`), but the risk that motivated writing the invariant in the
first place is independently covered by the completeness of `_CLUE_FUNCTION_NAMES`, which I verified
directly rather than taking on faith.

**Verdict: this is a genuine, but non-blocking, documentation/test-hygiene defect** — the docstring
overstates the fixture's layout, and by this phase's own standard (39-11's must_have: "a docstring
asserting something the code/fixture does not have is the same defect class as a stale test name"),
that overstatement should be corrected. It does **not** undermine the actual, substantive
verification that `danger`, `attention` and `error` resolve to three pairwise-distinct functions —
that claim is fully proven, independent of adjacency, by the completeness of the recognized-token
set. I classify it as WARNING (test-hygiene), not BLOCKER: it does not leave any must-have's
underlying claim unproven, only mis-described in prose. `39-REVIEW.md`'s own classification of this
as an INFO item is slightly more lenient than I would put it (I'd call it WARNING given the phase's
own stated standard equating a false docstring with a stale test name), but either classification
does not change the overall phase verdict — it is a documentation-accuracy carry-forward, not a gap.

### Human Verification Required

None. ADM-04 (the phase's only `[V]`-class requirement) has a recorded, operative human sign-off for
**both** tranches: the original 2026-08-02 verdict (MET, icon-shape grounds) and its dated amendment
under gap G-39-1 (re-taken against the post-reversal render, verdict: MET, owner's verbatim
"approved"). Per this verification task's explicit instructions, both verdicts are taken as given and
are not re-opened, re-rendered, or re-judged here.

### Gaps Summary

None blocking. Gap **G-39-1** (the deliberate D-03 reversal) is fully closed on live-run evidence:

- The routing change (`visit_danger`→`danger`, `visit_attention`→`memo`) is landed, minimal (13
  insertions / 8 deletions, confined to the two handlers and their docstrings), and independently
  re-confirmed by me via direct `grep`/read against `typsphinx/translator.py`.
- Both new gate modules (`test_admonition_bucket_render_gate.py`'s 2 new + 2 renamed tests,
  `test_admonition_locale_title_precedence_gate.py`'s 9 new tests) are green, re-run directly by me.
- ADM-04's sign-off was genuinely re-taken (not reused) against a post-reversal render whose bytes
  differ from the prior artifact, with a positive owner verdict naming the specific `attention`/
  `error` adjacency pair.
- The full-corpus `-b typstpdf` gate genuinely ran (not skipped) and passed, re-confirmed by me
  directly this session.
- The full suite (774 passed, 1 skipped, 0 failed) and the lint/type trio are clean, re-confirmed by
  me directly.
- Every planning-document amendment (`39-CONTEXT.md` D-03-R, `REQUIREMENTS.md` ADM-02,
  `ROADMAP.md` SC#1) is additive with the original wording preserved verbatim — confirmed by direct
  read, not assumed.
- Two WARNING-level, non-blocking findings carried forward or newly adjudicated (WR-01: a
  test-coverage gap in two renamed unit tests; IN-01: a docstring overstating fixture adjacency,
  adjudicated above as real but not undermining the underlying proof) plus one INFO-level style item
  (IN-02, unrelated pre-existing tooling nit). None blocks phase goal achievement.
- Truth #1's zero-call-site assertion inversion is a recorded, intentional design consequence
  (D-03-R), not a regression — preserved in this report's dedicated amendment section above and
  durably in `39-GAP-G39-1-CLOSEOUT.md`.

---

## Acknowledged Gate Overrides (carried forward from the pre-gap verification)

### 1. `api-coverage.verify-pre` — false positive, overridden by owner on 2026-08-02

**Gate output:** `block: true`, `detected: true`, signal on the prose token "api". Phase 39 integrates
zero external APIs; the firing text in every case refers to the project's own `docs/source/api/`
autodoc page or to `pypdf`'s in-process Python API (a dev/test dependency), never to a shipped
external-API integration. Owner reviewed and elected to continue as a false positive. No
`COVERAGE.md` was produced. Unaffected by the gap-closure tranche (no new API-surface signal
introduced by plans 39-09..39-13).

---

_Verified: 2026-08-02T06:00:00Z_
_Verifier: Claude (gsd-verifier)_
_This report supersedes the pre-gap `39-VERIFICATION.md` (2026-08-02T03:33:10Z) and its subsequent
in-place amendment; a pre-amendment backup of the prior file was recorded at
`.planning/backups/39-VERIFICATION.md.pre-G39-1-amendment.2026-08-02.bak` by plan 39-13 before this
regeneration._

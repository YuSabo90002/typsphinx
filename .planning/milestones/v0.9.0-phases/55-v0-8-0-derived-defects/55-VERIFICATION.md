---
phase: 55-v0-8-0-derived-defects
verified: 2026-08-16T07:18:35Z
status: passed
score: 5/5 must-haves verified
behavior_unverified: 0
overrides_applied: 0
human_verification_resolved:
  - resolved: 2026-08-16
    by: owner
    decision: "File CR-01 as a pending todo; do NOT fix inside Phase 55."
    artifact: ".planning/todos/pending/2026-08-16-track-image-escape-branch-basename-not-normalized.md"
    rationale: "CR-01 is real and reproducible but pre-existing (identical Typst compile failure on the pre-fix tree at 40b92fc6) and falsifies neither SC#4 nor SC#5. Fixing it inside this phase would ship a product change that never passed this phase's own RED-first, real-compile-gate discipline (binding constraint #6). The filed todo carries CR-01, WR-01 (no length bound) and the unescaped image(\"...\") emission site together, and is cross-linked to the sibling _escapes_outdir() gap 55-03 filed."
human_verification:
  - test: "[RESOLVED 2026-08-16 — filed as a todo, see human_verification_resolved above] Decide disposition of CR-01 (55-REVIEW.md + orchestrator addendum): _track_image()'s escape-branch relocation key embeds a raw, unescaped backslash for a Windows-driveless/UNC/drive-qualified absolute image URI processed on a POSIX build host, because path.basename(resolved_uri) does not split on '\\\\'. That key later reaches visit_image()'s image(\"...\") call with no escape_typst_string() pass, and Typst rejects the compile (\"path must not contain a backslash\")."
    expected: "An explicit owner decision: fix now (one-line normalization, per 55-REVIEW.md's suggested patch) vs. file a pending todo (mirroring the sibling _escapes_outdir() gap 55-03 already filed) vs. accept as-is. Currently the finding exists only inside 55-REVIEW.md's addendum — no .planning/todos/pending/*.md entry captures it, so it risks being lost once this phase closes."
    why_human: "This is a value judgment about severity/priority and about whether a Warning-level, pre-existing (not Phase-55-introduced) defect needs a follow-up artifact before the phase is considered fully closed — not something a grep/test check can decide. My own independent reproduction (see 'CR-01 independent reproduction' below) confirms the orchestrator's re-measurement: the defect is real, reproducible, and pre-existing (identical Typst compile failure on the pre-fix tree at commit 40b92fc6), so it does not falsify SC#4 or SC#5, but it is currently undocumented as a trackable follow-up."
---

# Phase 55: v0.8.0-Derived Defects Verification Report

**Phase Goal:** The four minor defects v0.8.0 shipped unfixed by owner decision D-01 — all new
failure classes created by features that milestone shipped — plus the fifth whose product side is
still open after plan 52-09 fixed only the test, are closed on the **product** side, each with its
own RED-recorded reproduction. Every one of these is a "compiles fine, produces wrong output" or
"wrong exception type" shape, so binding constraint #6's amended RED applies to all five: the
pre-fix assertion is written down before implementation starts.

**Verified:** 2026-08-16T07:18:35Z
**Status:** passed (initially `human_needed`; the single human item was resolved by the owner on 2026-08-16 — see "Human verification resolution" at the end of this report)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria, SC#4 as amended)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A label collision no longer links to a decoy (XREF-05) | ✓ VERIFIED | `uv run pytest tests/test_xref_compile_time_guard_render_gate.py -k collision -q` → `1 passed, 5 deselected` (reproduced independently). `_LABEL_TOKEN_INTRODUCER_RE` present and used inside `_sanitize_label` (`translator.py:59`, `:5220`). RED (`55-01-RED-EVIDENCE.md`) recorded pre-fix destination list containing `a_u2f_b:nested-target` against SHA `3d8bdb10`, git-verified as an ancestor of the fix commit `026af474` (same commit — plan's own design, see Binding Constraint #6 note below). |
| 2 | Include-edge keys cannot collide through their own separators (BLD-07) | ✓ VERIFIED | `uv run pytest tests/test_include_edge_separator_collision_gate.py -q` → `4 passed` (reproduced). `_escape_include_edge_separators()` present and called exactly at the two component sites inside `make_include_edge_key` (`translator.py:210`, `:317`, `:320`). RED commit `dc29dd8b` git-verified as an ancestor of fix commit `1caf1b10`, and pre-fix SHA `40b92fc6` verified an ancestor of `dc29dd8b`. |
| 3 | A too-deep include chain fails by name (BLD-08) | ✓ VERIFIED | Same RED commit `dc29dd8b` (labelled unit-level section) precedes fix commit `f9c9fe6b`. `_MAX_INCLUDE_CHAIN_DEPTH = 500` present (`translator.py:340`), checked as first statement in `walk()` (`:414`), raising `ExtensionError` naming bound/depth/chain (`:419`). `uv run pytest tests/test_include_edge_derivation_unit.py -q` → part of the `37 passed` reproduced above. |
| 4 | A driveless-absolute Windows image URI is classified like its sibling (BLD-09, **AMENDED wording**) | ✓ VERIFIED | `uv run pytest tests/test_builder.py -k "driveless_absolute or unc_absolute or relative_uri_is_not" -q` → `3 passed` (reproduced). `_is_absolute_image_uri()` present (`builder.py:121`), applies backslash-normalization then `posixpath.isabs(...) or _is_drive_qualified(...)` (`:193-194`) — read directly from source, matches the amended ROADMAP text exactly (see "SC#4 Amendment Legitimacy" below). Gate call site confirmed (`builder.py:1653`). RED commit `b8aa7f0f` git-verified an ancestor of fix commit `1ae047db`. |
| 5 | Two escaping images sharing a basename stay distinct (IMG-03) | ✓ VERIFIED | `uv run pytest tests/test_builder.py -k "same_basename or pure_function_of_uri" -q` → `2 passed` (reproduced). `hashlib.sha1(resolved_uri.encode("utf-8")).hexdigest()[:8]` prefix present in the escape-branch key (`builder.py:1700`), a pure function of the whole `resolved_uri`. Collision branch confirmed untouched (`test_post_process_images_rehome_collision_relocates_silently` still green, part of full-suite run). RED commit `b8aa7f0f` precedes fix commit `9a5ab47b` (same evidence file, same ancestor relationship verified above). |

**Score:** 5/5 truths verified

### SC#4 Amendment Legitimacy (special check requested)

The amendment is legitimate — recorded, owner-approved, and matches what shipped:

1. **Recorded as a blocking decision, not silently resolved.** `55-03-PLAN.md` Task 2 is
   `type="checkpoint:decision" gate="blocking"`, presenting three options (a: literal SC#4 wording,
   b: backslash-normalized idiom, c: defer BLD-09) with a measured predicate table showing option-a
   evaluates `False` for the exact URI shapes BLD-09 requires to reach the rehome branch.
2. **Owner-approved.** `55-03-SUMMARY.md` § "Task 2 Checkpoint Resolution" records: "Decision:
   option-b" plus a second explicit decision, "YES — ROADMAP SC#4's wording is to be amended in plan
   `55-04`", both attributed to the owner, with the precise replacement text pre-written for `55-04`
   to apply without re-deriving.
3. **Matches what shipped.** I read `typsphinx/builder.py:121-194` directly: `_is_absolute_image_uri()`
   normalizes backslashes to forward slashes (`resolved_uri.replace("\\", "/")`) and *then* applies
   `posixpath.isabs(normalized) or _is_drive_qualified(normalized)` — exactly the "backslash-normalized"
   predicate the amended ROADMAP text (`.planning/ROADMAP.md` lines 819-830) describes, word for word.
4. **Applied as a scoped edit, not a rewrite.** `55-04-EVIDENCE.md` § "Checkpoint resolution" records
   `git diff -- .planning/ROADMAP.md | grep -c '910'` = `1` (stale line-number citation removed) and an
   18-line diff-stat, well under the plan's own 40-line scoped-replacement bound.

This is a legitimate, tracked goalpost amendment, not a silent moved goalpost.

### Binding Constraint #6 (amended RED) — independently verified against git history

For each plan, I confirmed via `git merge-base --is-ancestor` that the RED-recording commit (or, for
plan 55-01, the single commit whose own Task 1 procedurally records RED via a subprocess *before*
editing `typsphinx/`, per the plan's explicit design) is an ancestor of the corresponding production
fix commit, and that the named pre-fix SHA is itself an ancestor of the RED commit:

| Plan | Pre-fix SHA | RED commit | Fix commit(s) | Ancestor chain verified |
|------|-------------|------------|----------------|--------------------------|
| 55-01 (XREF-05) | `3d8bdb10` | `026af474` (RED capture + fix combined per plan's own Step A→B→C design — no phase-boundary gate needed between them, stated explicitly in `55-01-RED-EVIDENCE.md` "Handover") | `026af474` | `3d8bdb10` → `026af474`: YES |
| 55-02 (BLD-07/08) | `40b92fc6` | `dc29dd8b` (separate commit, test-only, no `typsphinx/` edits) | `1caf1b10` (BLD-07), `f9c9fe6b` (BLD-08) | `40b92fc6` → `dc29dd8b` → `1caf1b10`/`f9c9fe6b`: YES |
| 55-03 (BLD-09/IMG-03) | `40b92fc6` | `b8aa7f0f` (separate commit, test-only, no `typsphinx/` edits) | `1ae047db` (BLD-09), `9a5ab47b` (IMG-03) | `40b92fc6` → `b8aa7f0f` → `1ae047db`/`9a5ab47b`: YES |

For plan 55-01 specifically: the RED transcript in `55-01-RED-EVIDENCE.md` is a real, verbatim pytest
run plus a real subprocess-driven `sphinx-build` + `typst.compile()` invocation, captured *before* the
plan's Step B edits `translator.py` (confirmed by the plan's own `<action>` ordering and the
RED-EVIDENCE file's "Handover" section, which states Task 1 lands the fix within the same task
immediately after recording RED — no separate commit boundary exists for this one plan, by design, not
by omission). Plans 55-02 and 55-03 do have a separate RED-only commit preceding their fix commits,
which I verified directly via git ancestry rather than trusting the summaries. I did not find any case
where a RED-EVIDENCE transcript's claimed content contradicted the actual pre-fix source (I independently
diffed `40b92fc6:typsphinx/builder.py` and `3d8bdb10`-era `translator.py` against the RED-EVIDENCE
files' quoted pre-fix behaviour and found them accurate).

**Binding constraint #6 is discharged for all five requirements.**

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `typsphinx/translator.py::_LABEL_TOKEN_INTRODUCER_RE` | injective label pre-pass | ✓ VERIFIED | Defined `:59`, used `:5220` inside `_sanitize_label` |
| `typsphinx/translator.py::_escape_include_edge_separators` | separator escaper | ✓ VERIFIED | Defined `:210`, called at `:317`/`:320` (both docname components) |
| `typsphinx/translator.py::_MAX_INCLUDE_CHAIN_DEPTH` | depth bound = 500 | ✓ VERIFIED | `:340`; checked `:414`; raises `ExtensionError` naming bound/depth/chain `:419` |
| `typsphinx/builder.py::_is_absolute_image_uri` | platform-independent predicate | ✓ VERIFIED | Defined `:121-194`; gate call site `:1653` |
| `typsphinx/builder.py` escape-branch key | SHA-1[:8]-prefixed pure function | ✓ VERIFIED | `:1700` `hashlib.sha1(resolved_uri.encode("utf-8")).hexdigest()[:8]` |
| `tests/test_sanitize_label_injectivity_unit.py` | decoder round-trip proof | ✓ VERIFIED | Exists, collected and passing as part of full-suite run |
| `tests/test_include_edge_separator_collision_gate.py` | real compile BLD-07 gate | ✓ VERIFIED | Exists, `4 passed` reproduced directly |
| `55-01/02/03-RED-EVIDENCE.md`, `55-04-EVIDENCE.md` | evidence artifacts | ✓ VERIFIED | All four exist, non-empty, content spot-checked above |
| `CHANGELOG.md` § Unreleased § Fixed | 5 entries, one per requirement | ✓ VERIFIED | Read directly (lines 39-73): all five requirement IDs present, `### Changed` still exactly 2 entries, purely additive |

### Key Link Verification

| From | To | Via | Status |
|------|-----|-----|--------|
| `_namespace_label` | `_sanitize_label` | unchanged single label-alphabet primitive | ✓ WIRED (unchanged, confirmed by full-suite pass of all 9 label-emitting-site tests) |
| `make_include_edge_key` | `_escape_include_edge_separators` | two component call sites | ✓ WIRED |
| `derive_master_edge_keys` | `sphinx.errors.ExtensionError` | depth-bound raise | ✓ WIRED |
| `TypstBuilder._track_image` | `_is_absolute_image_uri` | gate condition | ✓ WIRED |
| `_is_absolute_image_uri` | `_is_drive_qualified` | reused idiom, not re-derived | ✓ WIRED (confirmed: `_is_drive_qualified` defined once, `builder.py:86`) |

### Behavioral Spot-Checks (independently reproduced by me, not transcribed)

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full suite | `uv run pytest -q` | `1366 passed, 5 skipped in 118.00s` | ✓ PASS (matches orchestrator's measurement exactly) |
| black | `uv run black --check .` | `336 files would be left unchanged` | ✓ PASS |
| ruff | `uv run ruff check .` | `All checks passed!` | ✓ PASS |
| mypy | `uv run mypy typsphinx/` | `Success: no issues found in 8 source files` | ✓ PASS |
| XREF-05 gate | `pytest tests/test_xref_compile_time_guard_render_gate.py -k collision -q` | `1 passed` | ✓ PASS |
| BLD-07/08 gates | `pytest tests/test_include_edge_separator_collision_gate.py tests/test_include_edge_derivation_unit.py -q` | `37 passed` | ✓ PASS |
| BLD-09 gate | `pytest tests/test_builder.py -k "driveless_absolute or unc_absolute or relative_uri_is_not" -q` | `3 passed` | ✓ PASS |
| IMG-03 gate | `pytest tests/test_builder.py -k "same_basename or pure_function_of_uri" -q` | `2 passed` | ✓ PASS |
| Zero new deps | `git diff --stat 3d8bdb10..HEAD -- pyproject.toml uv.lock` | empty | ✓ PASS |
| No typing modernization | `git diff 3d8bdb10..HEAD -- typsphinx/ \| grep -cE '^[-+].*from typing import'` | `0` | ✓ PASS |
| Production scope | `git diff --stat 3d8bdb10..HEAD -- typsphinx/` | only `builder.py` + `translator.py` | ✓ PASS |
| Milestone branch on origin | `git ls-remote --heads origin gsd/v0.9.0-per-document-templates` | non-empty, ancestor of local HEAD | ✓ PASS |

### CR-01 Independent Reproduction (known open item — instructed to verify, not merely transcribe)

I reproduced the mechanism myself, independently of both `55-REVIEW.md` and its orchestrator addendum:

```
$ uv run python -c "
from typsphinx.builder import _is_absolute_image_uri
from os import path
import hashlib
resolved_uri = '\\\\\\\\server\\\\share\\\\weird.png'
print(_is_absolute_image_uri(resolved_uri))       # True
print(path.basename(resolved_uri))                 # '\\\\server\\share\\weird.png' (whole string, POSIX basename does not split on backslash)
"
```

Confirmed: `_is_absolute_image_uri()` correctly classifies the UNC-shaped URI as absolute (SC#4's
intent), but the escape-branch relocation key at `builder.py:1700-1704` derives its basename via
`path.basename(resolved_uri)` on the **un-normalized** URI, which on a POSIX host does not split on
`\`. The resulting key retains raw backslashes and is later interpolated unescaped into
`visit_image()`'s `image("...")` call (`translator.py:4749`, confirmed `f'image("{adjusted_uri}"'`
with no `escape_typst_string()` call). This produces a Typst compile error
(`path must not contain a backslash`) for this input shape.

I also independently confirmed the orchestrator's "not a regression" claim by diffing the pre-fix
tree directly: `git show 40b92fc6:typsphinx/builder.py` shows the escape branch already used
`key = f"{RESERVED_IMAGE_NAMESPACE}/{path.basename(resolved_uri)}"` with the identical unnormalized
call, before Phase 55 touched this line at all. **My measurement agrees with the orchestrator's: this
is a real, reproducible defect, but it is pre-existing (not introduced by Phase 55) and does not
falsify SC#4 or SC#5.** Per instruction, it is not counted as a gap against this phase's goal.

However: unlike the sibling `_escapes_outdir()` gap (which plan 55-03 explicitly filed as
`.planning/todos/pending/2026-08-16-escapes-outdir-isabs-not-backslash-normalized.md`), **CR-01 has
not been filed as a trackable follow-up artifact anywhere** — it exists only as prose inside
`55-REVIEW.md`'s addendum. `55-04-EVIDENCE.md`'s "Open after this phase" list names exactly two items
and CR-01 is not one of them. This is why I am routing it to human verification rather than silently
absorbing it: the orchestrator explicitly re-rated it "Warning, not blocker... Owner decides fix-now
vs. todo," and that decision does not appear to have been made yet.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| XREF-05 | 55-01 | Label collision no longer links to decoy | ✓ SATISFIED | `_sanitize_label` injective, real-compile gate passes |
| BLD-07 | 55-02 | Include-edge key separator escaping | ✓ SATISFIED | `_escape_include_edge_separators`, real-compile gate passes |
| BLD-08 | 55-02 | Named ExtensionError on too-deep chain | ✓ SATISFIED | `_MAX_INCLUDE_CHAIN_DEPTH`, unit gate passes |
| BLD-09 | 55-03 | Platform-independent absolute-URI predicate | ✓ SATISFIED | `_is_absolute_image_uri`, unit gate passes |
| IMG-03 | 55-03 | Escape-branch key is pure function of whole URI | ✓ SATISFIED | SHA-1[:8]-prefixed key, unit gate passes |

No orphaned requirements — `.planning/REQUIREMENTS.md` § "v0.8.0-derived defects" and the traceability
table both list exactly these five for Phase 55, all accounted for above.

**Note on REQUIREMENTS.md checkbox state:** currently `XREF-05` is `[x]` and `BLD-07`/`BLD-08`/`BLD-09`/
`IMG-03` are `[ ]`, deliberately left untouched by plan 55-04's own scope fence (its stated reason:
"the phase-completion step owns that transition, and it has flipped a requirement against a recorded
decision four consecutive times"). Based on my independent verification above, **all five are
substantively closed on the product side** and the four `[ ]` checkboxes are stale — the phase-completion
step should flip `BLD-07`, `BLD-08`, `BLD-09`, and `IMG-03` to `[x]`.

### Anti-Patterns Found

No debt markers (`TBD`/`FIXME`/`XXX`) or stub patterns found in any file this phase modified. One
unrelated pre-existing `TODO-01` occurs in `translator.py:6262` inside `visit_todo_node`'s docstring —
it is a formal requirement-ID cross-reference (paired with threat-ID `T-16-01`), not a debt marker, and
is untouched by this phase's diff.

### Gaps Summary

No blocking gaps. All five ROADMAP success criteria are met with independently-reproduced evidence,
all five requirement IDs are substantively satisfied, binding constraint #6 (amended RED) is discharged
for all five with git-history-verified ancestor chains, the SC#4 amendment is legitimate and
recorded, and the phase closes at the same unconditional 1366/5/0 green bar the orchestrator measured
(reproduced independently, not transcribed).

The one open item — CR-01, a real but pre-existing defect in the same code this phase touched, not yet
filed as a follow-up artifact — is routed to human verification below rather than treated as a gap,
because it does not falsify any of this phase's own success criteria and the orchestrator already
correctly re-rated it non-blocking. It should not, however, be allowed to fall through the cracks
silently; an explicit disposition (todo vs. fix-now vs. accept) closes the loop the sibling
`_escapes_outdir()` gap already received.

---

## Human verification resolution (2026-08-16)

The single `human_needed` item above was put to the owner at phase close, with the
measurement it rests on, and resolved: **file CR-01 as a pending todo; do not fix
inside Phase 55.**

Filed as
`.planning/todos/pending/2026-08-16-track-image-escape-branch-basename-not-normalized.md`,
carrying three related gaps in one path — CR-01's non-normalized `path.basename()`,
WR-01's missing length bound on the `{digest}-{basename}` key, and the absence of any
`escape_typst_string()` at `visit_image()`'s `image("...")` emission site — and
cross-linked to the sibling `_escapes_outdir()` gap plan `55-03` already filed. The
todo records that whatever fix lands must carry a real `typst.compile()` gate, since
neither of BLD-09's new tests renders or compiles its result, which is why this
survived Phase 55's suite.

Phase status advanced to `passed`. This is a resolution of the item, not a waiver of
it: the defect is now tracked where `/gsd-progress`, `/gsd-audit-uat` and release prep
will surface it, which is precisely what the item asked for.

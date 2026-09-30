# Phase 42, Plan 06 — SC#4 Milestone-Invariant Sweep Re-Measured Over a Range Including Phase 42

**Recorded:** 2026-08-03T14:53:15Z, inside worktree-agent worktree `worktree-agent-a487e99b3ae6ae3cd`.

This file re-measures ROADMAP SC#6's second obligation: `41-SC4-INVARIANTS.md` proved the
milestone invariants over `51e02b6b61b314c99740883fb4bee7ce7b9be76b..aa9d2f06ad854f6f96d285d669ba4bb91b053f31`
(Phase 41's own tip) — a range that ends **before** Phase 42's `depart_table` fix landed. This file
re-measures the same invariants over the SAME BASE but a NEW HEAD: this worktree's own tip, which
includes Phase 42's commits. Every number below is transcribed verbatim from a command actually run
in THIS worktree; nothing here is copied from `41-SC4-INVARIANTS.md`, `41-CONTEXT.md`,
`41-RESEARCH.md`, or any Phase 42 evidence file's own prior prose — those record earlier
measurements of overlapping-but-not-identical quantities.

**What this file supersedes, and what it does not.** `41-SC4-INVARIANTS.md` remains the correct
record for the range it measured (`BASE..aa9d2f0`) — it is not wrong, it was scoped to a tree that
did not yet contain Phase 42. This file is the record for the range that includes Phase 42
(`BASE..HEAD` as measured below). Per `42-CONTEXT.md`'s Claude's-Discretion section, this
reconciliation lives in a **new** file under this phase's own directory; `41-SC4-INVARIANTS.md` is
read-only source material here, never edited, appended to, or regenerated.

---

## Diff-range re-measurement (source of truth)

Same BASE as Phase 41, re-derived rather than trusted:

```
$ git describe --tags 51e02b6b61b314c99740883fb4bee7ce7b9be76b
v0.6.5-1-g51e02b6
```

`describe` confirms the BASE is still exactly **one commit past the `v0.6.5` tag** — the same
relationship `41-SC4-INVARIANTS.md` recorded, re-derived here rather than transcribed.

```
$ git rev-parse HEAD
d57f6d1f27355a408daa20d8d06ba42cb5e3a5d6

$ git log --oneline 51e02b6b61b314c99740883fb4bee7ce7b9be76b..d57f6d1f27355a408daa20d8d06ba42cb5e3a5d6 | wc -l
460
```

**The commit count measured right now is 460.** Per `41-RESEARCH.md` Pitfall 3 (carried into
`41-SC4-INVARIANTS.md`'s own note), this number is a moving target on an actively developed branch —
Phase 41's own sweep recorded 394 for its own HEAD (`aa9d2f0`, a strictly earlier tip than this
plan's). **460 is a newer value than Phase 41's 394**, and this file's own HEAD (`d57f6d1`) is
itself a moving target — by the time this plan's own SUMMARY.md and metadata commits land, `HEAD`
will have advanced past `d57f6d1` again. `BASE` for every command below is
`51e02b6b61b314c99740883fb4bee7ce7b9be76b`; `HEAD` is `d57f6d1f27355a408daa20d8d06ba42cb5e3a5d6`
(this plan's Task 1 commit — the tip at the moment this task's measurements were taken).

### Proving Phase 42 is inside the range (the reason this file exists at all)

```
$ git merge-base --is-ancestor e5575f3ab51144405c44764a5b192b9d5f7526b2 d57f6d1f27355a408daa20d8d06ba42cb5e3a5d6 && echo "e5575f3 IS in range"
e5575f3 IS in range
```

`e5575f3` is plan 42-04's fix commit (`fix(42-04): move captioned-table propagated-anchor call past
in-table reset`, per `42-GATE-EVIDENCE-04.md` § 1). `git merge-base --is-ancestor` exits `0` (proof,
not assertion) that this commit is an ancestor of the current HEAD.

```
$ git log --oneline 51e02b6b61b314c99740883fb4bee7ce7b9be76b..d57f6d1f27355a408daa20d8d06ba42cb5e3a5d6 -- typsphinx/translator.py
e5575f3 fix(42-04): move captioned-table propagated-anchor call past in-table reset
c81ca29 fix(41-03): escape the unbalanced asterisk in visit_desc_sig_name's docstring (D-12)
41d2683 fix(40.1-03): promote D-14 anchor decision into one shared predicate
9928f93 fix(40.1-02): widen citation run-adjacency skip list for ids-less targets
e8d4f42 fix(40.1-01): fail-closed WR-01 backref filter in visit_citation
12a2bee feat(40-03): implement citation definition handlers (D-01..D-08, D-13, SC#5)
927431d feat(40-03): give a citation-derived reference its own anchor (D-14)
0430d47 feat(39-11): re-route danger and attention to their own gentle-clues ids
5a45b20 fix(39-06): stop visit_rubric double-counting the id-anchor separator (D-11)
db70c2a fix(39-06): give visit_rubric/depart_rubric their own save slots (D-13)
ecf5ab7 feat(39-05): source static admonition titles from sphinx.locale.admonitionlabels
a6c04ea feat(39-05): re-route five admonition call sites to their new buckets
e7a27ab feat(38-09): reorder FLD-02 branch ahead of D-13 list-item fast-path
4c71600 feat(38-07): give literal_strong/literal_emphasis their own monospace leaves
7f7f247 fix(38-06): route depart_desc_signature's anchor/spacing appends through add_text
d55df99 feat(38-06): render a single-value field body inline with its label
16920ba feat(38-06): give field_list its own indent step nested in the body wrapper
8db1899 fix(38-05): make the SIG-08 break marker buffer-identifying
3b9564e feat(38-05): wrap desc_content in shared indent step, propagate D-10 marker
76324bf fix(37-09): drop the zeroed above/below override on the signature wrapper
6c1d63b feat(37-07): emit a real return-arrow glyph (SIG-06)
816e252 feat(37-07): place D-11 optional-group separator inside its bracket
7c8dce0 feat(37-07): swap parameter-list delimiters to monospace primitive
f63fe8f feat(37-06): bold desc_name/desc_annotation, italic parameter names (D-05)
7674e3f feat(37-06): route signature text through the monospace primitive
550b04a feat(37-06): compose block+par desc_signature wrapper for SIG-07/SIG-09
ebf7e18 fix(37-05): suppress depart_desc's duplicate parbreak() for nested desc (SIG-08)
995c78d fix(36-03): clear list_item_needs_separator after block math, close MATH-02
8708ab0 feat(36-02): decouple visit_rubric/depart_rubric from visit_strong
12547a2 feat(36-02): decouple visit_desc_signature/depart_desc_signature from visit_strong
```

`e5575f3` is the ONLY commit in this range whose subject line names Phase 42 (`42-04`), and it is the
newest (topmost) commit touching `typsphinx/translator.py` in the whole range. Every other commit
listed pre-dates Phase 42 and was already inside `41-SC4-INVARIANTS.md`'s own measured range — this
matches this plan's own `<measured_state>`: "the only production-source change in Phase 42 is
`typsphinx/translator.py`, in exactly one commit."

---

## Invariant 1 — zero new runtime dependencies

```
$ git diff --stat 51e02b6b61b314c99740883fb4bee7ce7b9be76b..d57f6d1f27355a408daa20d8d06ba42cb5e3a5d6 -- pyproject.toml
 pyproject.toml | 3 ++-
 1 file changed, 2 insertions(+), 1 deletion(-)

$ git diff --stat 51e02b6b61b314c99740883fb4bee7ce7b9be76b..d57f6d1f27355a408daa20d8d06ba42cb5e3a5d6 -- uv.lock
 uv.lock | 75 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 74 insertions(+), 1 deletion(-)
```

Both diffs are **byte-identical in shape and size** to the ones `41-SC4-INVARIANTS.md` § "Invariant
1" recorded over its own (shorter) range — confirming Phase 42 contributes zero additional lines to
either file:

```
$ git diff 51e02b6b61b314c99740883fb4bee7ce7b9be76b..d57f6d1f27355a408daa20d8d06ba42cb5e3a5d6 -- pyproject.toml
diff --git a/pyproject.toml b/pyproject.toml
index 82b1efc..d50c6b0 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -4,7 +4,7 @@ build-backend = "setuptools.build_meta"

 [project]
 name = "typsphinx"
-version = "0.6.5"
+version = "0.7.0"
 description = "Sphinx extension for Typst output"
 readme = "README.md"
 requires-python = ">=3.12"
@@ -44,6 +44,7 @@ dev = [
     "twine>=5.0",
     "build>=1.0",
     "pypdf>=6.14,<7",
+    "pillow>=12.3,<13",  # D-07: ADM-04 greyscale render (Image.convert), dev-only
 ]
 docs = [
     "furo>=2024.0",
```

Two hunks, attributed hunk by hunk (neither is Phase 42's):

- Hunk 1 (`version = "0.6.5"` -> `"0.7.0"`) — Phase 41 plan 41-02's version bump (`d4a603d`).
- Hunk 2 (`pillow` added to the `dev` extra) — Phase 39's D-07 addition (`a5be0b9`), pre-dating both
  Phase 41 and Phase 42.

```
$ git diff 51e02b6b61b314c99740883fb4bee7ce7b9be76b..d57f6d1f27355a408daa20d8d06ba42cb5e3a5d6 -- uv.lock | grep -E '^[+-]name = |^[+-]version = '
+name = "pillow"
+version = "12.3.0"
-version = "0.6.5"
+version = "0.7.0"
```

Only `pillow`'s lock entry (Phase 39) and `typsphinx`'s own version field (Phase 41) move. No
third-party package's pinned version moves anywhere in `uv.lock`.

**Phase 42's own contribution confirmed empty:**

```
$ git log --oneline 51e02b6b61b314c99740883fb4bee7ce7b9be76b..d57f6d1f27355a408daa20d8d06ba42cb5e3a5d6 -- pyproject.toml uv.lock
d4a603d chore(41-02): bump version to 0.7.0 across pyproject, README, and uv.lock
a5be0b9 feat(39-04): add pillow to dev extra for ADM-04 greyscale render

$ git show e5575f3ab51144405c44764a5b192b9d5f7526b2 --stat
commit e5575f3...
 typsphinx/translator.py | 34 +++++++++++++++++++++++++++-------
 1 file changed, 27 insertions(+), 7 deletions(-)
```

Neither commit in the `pyproject.toml`/`uv.lock` log carries a `42-` prefix, and Phase 42's own fix
commit (`e5575f3`) touches only `typsphinx/translator.py`. **Milestone invariant #1 is mechanically
discharged for Phase 42: no dependency was added by this phase.**

### Verdict — Invariant 1

**PROVEN, unchanged from Phase 41's own PARTIAL-with-explained-deviation verdict, because Phase 42
contributes nothing to either file.** The runtime `dependencies` array is unaffected (not
re-diffed here since the diff-stat above shows only the two pre-existing hunks with zero new lines);
the one dev-only `pillow` addition remains a pre-existing Phase 39 fact, not a Phase 42 contribution.

---

## Invariant 2 — the `@preview` surface stays at four, no new lockstep site

```
$ grep -n "@preview" typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ
typsphinx/writer.py:155:            imports.append('#import "@preview/codly:1.3.0": *')
typsphinx/writer.py:156:            imports.append('#import "@preview/codly-languages:0.1.10": *')
typsphinx/writer.py:157:            imports.append('#import "@preview/mitex:0.2.7": mi, mitex')
typsphinx/writer.py:158:            imports.append('#import "@preview/gentle-clues:1.3.1": *')
typsphinx/templates/base.typ:8:#import "@preview/codly:1.3.0": *
typsphinx/templates/base.typ:9:#import "@preview/codly-languages:0.1.10": *
typsphinx/templates/base.typ:14:#import "@preview/mitex:0.2.7": *
typsphinx/templates/base.typ:19:#import "@preview/gentle-clues:1.3.1": *
typsphinx/template_engine.py:225:            typst_package: Typst Universe package specification (e.g., "@preview/charged-ieee:0.1.0")
typsphinx/template_engine.py:612:            output_parts.append('#import "@preview/codly:1.3.0": *')
typsphinx/template_engine.py:613:            output_parts.append('#import "@preview/codly-languages:0.1.10": *')
typsphinx/template_engine.py:614:            output_parts.append('#import "@preview/mitex:0.2.7": mi, mitex')
typsphinx/template_engine.py:615:            output_parts.append('#import "@preview/gentle-clues:1.3.1": *')
```

Same four package names, same four version strings, same line numbers as `41-SC4-INVARIANTS.md`
recorded for its own (shorter) range.

```
$ git diff --stat 51e02b6b61b314c99740883fb4bee7ce7b9be76b..d57f6d1f27355a408daa20d8d06ba42cb5e3a5d6 -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ
(no output)
```

**Byte-identical across the entire range including Phase 42** — none of the three sync sites
changed by a single line since `BASE`. Phase 42's own fix commit touches only `depart_table`'s call
ordering inside `typsphinx/translator.py`, a file with no `@preview` declaration.

```
$ git diff --diff-filter=A --name-only 51e02b6b61b314c99740883fb4bee7ce7b9be76b..d57f6d1f27355a408daa20d8d06ba42cb5e3a5d6 -- typsphinx/ examples/
(no output)
```

No file was newly added under `typsphinx/` or `examples/` anywhere in the range — a strict superset
check of `41-SC4-INVARIANTS.md`'s own finding (that sweep found the same empty result over its
shorter range; extending the range through Phase 42 does not change it, because Phase 42 added no
file under either directory — it added fixtures and test modules under `tests/` only, per the
`artifacts_this_phase_produces` census in `42-06-PLAN.md`).

```
$ uv run pytest tests/test_preview_version_sync.py -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a487e99b3ae6ae3cd
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 3 items

tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 33%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 66%]
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED [100%]

============================== 3 passed in 0.01s ===============================
```

### Verdict — Invariant 2

**PROVEN.** All three declaration sites remain line-for-line identical to `BASE`; no new production
`@preview` site was introduced anywhere in the range, including by Phase 42; the drift-guard test
passes.

---

## Invariant 4 — every node-handler change carries its recorded-RED GATE-01 fixture (the clause that grows)

Per `REQUIREMENTS.md` § "Milestone invariants" #4, GATE-01 RED for this milestone is redefined
(structural/regex/`pypdf`-text, not the classic compile fatal), with **CIT-01 and TBL-03** named as
the milestone's two exceptions that keep the classic `typst.compile()` fatal RED. This section
proves TBL-03's exception is real and traceable, extending `41-SC4-INVARIANTS.md`'s own "Invariant 3
of 3" section (which measured this same clause over a range ending before TBL-03 existed).

### Phase 42's `depart_table` commit, re-confirmed inside the range

```
$ git show e5575f3ab51144405c44764a5b192b9d5f7526b2 -- typsphinx/translator.py
```

(Full diff quoted in `42-GATE-EVIDENCE-04.md` § 2; not re-quoted here — that file is this phase's
own evidence, not a `41-*` artifact, and re-transcribing a large diff a sibling evidence file already
carries verbatim would not add measurement value.) The commit's `--stat` (already shown above under
Invariant 1) confirms: `typsphinx/translator.py | 34 +++++++++++++++++++++++++++-------`, `1 file
changed, 27 insertions(+), 7 deletions(-)` — the ONLY production file touched, matching D-05's "the
fix is a call-ordering change inside the table departure handler only."

### RED-to-GREEN commit ordering, re-verified in this worktree

```
$ git merge-base --is-ancestor d28f2c8bcdf8aee49ab82b1d883145a4036acefc e5575f3ab51144405c44764a5b192b9d5f7526b2 && echo "d28f2c8 (RED) IS ancestor of e5575f3 (fix)"
d28f2c8 (RED) IS ancestor of e5575f3 (fix)

$ git log -1 --format="%H %s" d28f2c8bcdf8aee49ab82b1d883145a4036acefc
d28f2c8bcdf8aee49ab82b1d883145a4036acefc test(42-01): record classic RED for captioned-table propagated-target drop
```

The RED was recorded in its own earlier commit, against unfixed source (`42-GATE-EVIDENCE-01.md` § 1
confirms `git status --porcelain typsphinx/` was empty at that commit), and the fix landed
separately and later — the exact ordering milestone invariant #4 requires for a classic-RED
exception.

### Change-site to RED manifest (Phase 40.1's `40.1-NONREGRESSION.md` § 4 column shape)

| # | Change site (function/symbol) | Requirement | Evidence file | RED form | RED provenance (reason) | Pytest selector (RED) | Commit the RED was recorded against |
|---|-------------------------------|-------------|----------------|----------|---------------------------|------------------------|---------------------------------------|
| 1 | `depart_table`'s propagated-anchor call ordering (`was_captioned`-gated `_emit_id_anchors` move past `self.in_table = False`) | TBL-03 | `42-GATE-EVIDENCE-01.md` § 4 | classic `typst.compile()` fatal (`TypstError: label \`<index:tbl-target>\` does not exist in the document`) | **real `sphinx-build -b typstpdf`** — the fixture's own `.. _tbl-target:` standalone target immediately preceding a `:name:`-carrying captioned table, reproduced as an actual PDF-compile failure, not a directly-assembled doctree | `uv run pytest tests/test_captioned_table_propagated_target_render_gate.py::TestCaptionedTablePropagatedTargetRenderGate::test_compile_clean -v` | `d28f2c8` (`test(42-01): record classic RED for captioned-table propagated-target drop`) |

**RED-to-GREEN commit reference, for completeness (not a fifth column — matching
`40.1-NONREGRESSION.md`'s own "not a fifth column" framing):**

| Requirement | GREEN commit |
|-------------|--------------|
| TBL-03 | `e5575f3` (`fix(42-04): move captioned-table propagated-anchor call past in-table reset`) |

**Why one row is sufficient.** `depart_table` is the only `visit_`/`depart_`-prefixed handler
touched by Phase 42's own commit (confirmed by the `--stat` above: one file, one hunk region,
`depart_table`'s body per `42-GATE-EVIDENCE-04.md` § 2's diff). Unlike Phase 40.1 (which touched
three functions plus one deletion across three commits), Phase 42 is a single call-ordering move
inside a single handler in a single commit — the manifest has exactly the number of rows the diff
supports, not a placeholder count.

**The RED covers four failing shapes, not one.** `test_compile_clean` is the row's selector because
it is the assertion that most directly names "compiles" (the classic-RED contract), but the same RED
commit (`d28f2c8`) also recorded three sibling shape-specific tests failing for the same underlying
defect (`test_shape_a_named_target_anchor` through `test_shape_d_two_consecutive_targets_anchor`,
per `42-GATE-EVIDENCE-01.md` § 4: "7 of 9 tests are RED"). All four ride the same recording commit
and the same evidence file; a single manifest row is faithful to that — the manifest's contract, per
`40.1-NONREGRESSION.md`'s own framing, is the RED's existence and provenance, not an enumeration of
every assertion it backs.

### Why TBL-03 is the second classic-RED exception, not a violation of invariant 4's own redefinition

`REQUIREMENTS.md` names TBL-03 alongside CIT-01 as the milestone's two classic-RED exceptions,
because both fail the compile **today**, unlike every other v0.7.0 requirement (which compiles
successfully but renders wrong). The manifest row above is the mechanical proof of that exception
being honoured: RED form is explicitly `classic typst.compile() fatal`, not structural/regex/`pypdf`
— exactly what the exception permits and nothing else in the milestone's redefinition would allow.

### Verdict — Invariant 4

**PROVEN.** The change-site-to-RED manifest carries one row for Phase 42's sole node-handler change
(`depart_table`), with RED form, provenance, pytest selector, and recording commit all resolving to
real, existing artifacts — `git cat-file -e d28f2c8bcdf8aee49ab82b1d883145a4036acefc` and `git
cat-file -e e5575f3ab51144405c44764a5b192b9d5f7526b2` both resolve (verified below), and the file
`42-GATE-EVIDENCE-01.md` exists at the path named in the table.

```
$ git cat-file -e d28f2c8bcdf8aee49ab82b1d883145a4036acefc && echo "d28f2c8 resolves"
d28f2c8 resolves
$ git cat-file -e e5575f3ab51144405c44764a5b192b9d5f7526b2 && echo "e5575f3 resolves"
e5575f3 resolves
$ test -f .planning/phases/42-captioned-table-drops-preceding-target-label/42-GATE-EVIDENCE-01.md && echo "FOUND"
FOUND
```

**This is the clause that actually grew, per this plan's own objective.** `41-SC4-INVARIANTS.md`'s
"Invariant 3 of 3" section measured this clause over a 51-handler census that did NOT include
`depart_table`'s Phase 42 change (its own HEAD, `aa9d2f0`, pre-dates `e5575f3`). This file adds
exactly the one row Phase 42 contributes; it does not re-derive Phase 41's 51-handler census, which
remains valid for the range it measured.

---

## Invariant 5 — test migration owned per phase

Phase 42's own test files, added or touched since the phase's base commit (`19a6378`, the last
commit before plan 42-01's first commit `b2a3564`):

```
$ git diff --stat 19a6378..d57f6d1f27355a408daa20d8d06ba42cb5e3a5d6 -- tests/
 tests/fixtures/captioned_table_propagated_target_render_gate/conf.py             |  40 +++
 tests/fixtures/captioned_table_propagated_target_render_gate/index.rst           |  97 ++++++
 tests/fixtures/figure_propagated_target_render_gate/conf.py                      |  40 +++
 tests/fixtures/figure_propagated_target_render_gate/image.png                    | Bin 0 -> 68 bytes
 tests/fixtures/figure_propagated_target_render_gate/index.rst                    |  55 ++++
 tests/test_captioned_table_propagated_target_render_gate.py                      | 347 +++++++++++++++++
 tests/test_figure_propagated_target_render_gate.py                               | 283 +++++++++++++
 7 files changed, 862 insertions(+)
```

Two new test modules (`test_captioned_table_propagated_target_render_gate.py`,
`test_figure_propagated_target_render_gate.py`) and two new fixture directories — no existing test
module's assertions were rewritten or invalidated by Phase 42 (the fix is additive: it makes a
previously-fatal compile succeed; it does not change any already-passing assertion's expected
output, confirmed by `42-GATE-EVIDENCE-04.md` § 5's `821 passed, 1 skipped` full-suite re-run with
zero new failures and the explicit `38 passed` re-run of the existing table/figure gate modules
`test_pdf_render_gate.py` and `test_figure_propagated_target_render_gate.py`). Per milestone
invariant #5's own wording ("owned per phase, never deferred to a single blanket closing pass"),
Phase 42 owns its own two new modules; it inherits no test-fix debt from any other phase.

### Verdict — Invariant 5

**PROVEN.** Phase 42's test additions are recorded exactly as the `artifacts_this_phase_produces`
census in `42-06-PLAN.md` names them; nothing outside `tests/` (and the `depart_table` production
change already covered under Invariant 4) was touched by this phase's test surface.

---

## Invariant 6 — "anywhere under X" success criteria checked by repo-wide grep

Per `REQUIREMENTS.md` § "Milestone invariants" #6, any success criterion phrased as "anywhere under
X" must be checked by a repo-wide grep at discovery time, not scoped to the files a requirement
happens to name.

**No Phase 42 success criterion is phrased that way.** A grep of `ROADMAP.md`'s Phase 42 section
(SC#1 through SC#6, quoted in full in `42-06-PLAN.md`'s own `<files_to_read>` chain) and
`REQUIREMENTS.md`'s TBL-03 entry finds no "anywhere under" wording:

```
$ grep -n "anywhere under" .planning/ROADMAP.md .planning/REQUIREMENTS.md
(no output)
```

This is not the same claim as "no repo-wide sweep happened this phase" — plan 42-03 DID run a
repo-wide sweep for the same misrouting class (D-06/D-07, recorded in `42-GATE-EVIDENCE-03.md`), but
that sweep was scoped by D-06's own explicit owner condition ("sweep everywhere, but only an
image-path finding gets fixed inside this phase"), not by invariant #6's "anywhere under X" success
criterion trigger. Invariant #6 is a specific textual trigger this phase's criteria never used; the
repo-wide sweep that DID happen is independently justified and independently evidenced, and is not
double-counted here as invariant #6's discharge.

### Verdict — Invariant 6

**NOT APPLICABLE.** No Phase 42 criterion is of the "anywhere under X" shape; the invariant imposes
no obligation on this phase to re-check.

---

## SC#4 verdict (this phase's re-measurement)

| Invariant | What was measured | Verdict |
|---|---|---|
| 1 — zero new runtime dependencies | `pyproject.toml` / `uv.lock` diffs over `BASE..HEAD` (this file's HEAD, including Phase 42) | **PROVEN** for Phase 42's own contribution (zero); the pre-existing Phase 39 `pillow` dev-extra addition and Phase 41 version bump are unchanged carried facts, exactly as `41-SC4-INVARIANTS.md` found |
| 2 — the `@preview` surface | All three declaration sites, byte-identical to `BASE`; no new file under `typsphinx/`/`examples/`; `test_preview_version_sync.py` re-run | **PROVEN** — unaffected by Phase 42 |
| 4 — every node-handler change carries its recorded-RED GATE-01 fixture (classic-RED exception, TBL-03) | Change-site to RED manifest, one row for `depart_table`, RED/GREEN commit ancestry re-verified, evidence file and both commits confirmed to resolve | **PROVEN** — this is the clause Phase 42 actually grows, discharged with its own new row |
| 5 — test migration owned per phase | Phase 42's own two new test modules and two new fixtures, no existing assertion rewritten | **PROVEN** |
| 6 — "anywhere under X" repo-wide grep | No Phase 42 criterion uses that phrasing | **NOT APPLICABLE** |

**No invariant is NOT PROVEN.** Invariants 1, 2, 4, and 5 are proven for the range including Phase
42; invariant 6 does not apply to this phase's own criteria. Invariants 1/2's "Invariant 3" numbering
from `41-SC4-INVARIANTS.md` and this file's "Invariant 4" both refer to the same
`REQUIREMENTS.md`-numbered milestone invariant #4 — this file uses the `REQUIREMENTS.md` numbering
(1, 2, 4, 5, 6) directly rather than `41-SC4-INVARIANTS.md`'s own internal "1 of 3 / 2 of 3 / 3 of 3"
relabeling, to keep this file's invariant numbers traceable to their source without a translation
step.

### Executed versus skipped — a skip is not a pass

| Command | Executed? | Skipped anything? |
|---|---|---|
| `git describe --tags` / `git rev-parse HEAD` / commit count | Yes — all ran, fresh values recorded | None |
| `git merge-base --is-ancestor` (fix commit in range; RED ancestor of fix) | Yes — both ran, both confirmed | None |
| `git log ... -- typsphinx/translator.py` (full range) | Yes | None |
| `git diff --stat` / full diff — `pyproject.toml`, `uv.lock` | Yes | None |
| `git log ... -- pyproject.toml uv.lock` (attribution) | Yes | None |
| `git show e5575f3 --stat` | Yes | None |
| `grep -n "@preview"` (3 files) / `git diff --stat` (3 files) | Yes | None |
| `git diff --diff-filter=A --name-only ... \| ` (typsphinx/, examples/) | Yes (empty result, confirmed) | None |
| `uv run pytest tests/test_preview_version_sync.py -v` | Yes — all 3 collected ran | None — 3 passed |
| `git cat-file -e` (×2, RED and fix commits) | Yes — both ran | None — both resolved |
| `test -f` (evidence file existence) | Yes | None |
| `git diff --stat 19a6378..HEAD -- tests/` | Yes | None |
| `grep -n "anywhere under"` (ROADMAP.md, REQUIREMENTS.md) | Yes (empty result, confirmed) | None |

**No command in this file returned a skip standing in for a pass.**

---

## Scratch tooling confirmation

No scratch script was needed for this file — every measurement is a direct `git`/`grep`/`pytest`
command, unlike `41-SC4-INVARIANTS.md`'s Invariant 3, which required a hunk-attribution census
script because it re-derived the full 51-handler list from scratch. This file adds one row to that
manifest rather than re-running the census, so no scratch tooling exists to confirm clean.

```
$ git status --porcelain -- typsphinx tests scripts
(no output)
```

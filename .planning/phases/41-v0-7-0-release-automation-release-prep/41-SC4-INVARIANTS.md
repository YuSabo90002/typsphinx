# Phase 41, Plan 06 — SC#4 Milestone-Invariant Proof

**Recorded:** 2026-08-03T11:39:01Z, inside a worktree-agent worktree for this plan
(`worktree-agent-a42d10f0bf8d257ce`).

This file proves ROADMAP SC#4 mechanically over the SHA-anchored full milestone diff. Per this
plan's own rule (measurement integrity), every number below is transcribed verbatim from a command
actually run in this worktree — nothing here is copied from `41-CONTEXT.md`, `41-RESEARCH.md`, or
any earlier phase's evidence file, all of which record earlier (now-stale) measurements of the same
quantities.

---

## Diff-range re-measurement (source of truth)

```
$ git merge-base main HEAD
51e02b6b61b314c99740883fb4bee7ce7b9be76b
```

```
$ git describe --tags 51e02b6b61b314c99740883fb4bee7ce7b9be76b
v0.6.5-1-g51e02b6
```

`describe` confirms the milestone base is exactly **one commit past the `v0.6.5` tag** — the same
relationship `41-RESEARCH.md` recorded (there as `51e02b6`), re-derived here rather than transcribed.

```
$ git rev-parse HEAD
aa9d2f06ad854f6f96d285d669ba4bb91b053f31
```

```
$ git log --oneline 51e02b6b61b314c99740883fb4bee7ce7b9be76b..aa9d2f06ad854f6f96d285d669ba4bb91b053f31 | wc -l
394
```

**The commit count measured right now is 394.** Per `41-RESEARCH.md` Pitfall 3, this number is a
moving target on an actively developed branch — CONTEXT.md recorded 328, the research session
re-measured 369, and a later research-session re-measurement gave 371. **394 is a fourth, newer
value; none of 328/369/371 is transcribed here as current, and 394 itself will already be stale by
the time a later plan in this same wave/phase re-measures it.** `BASE` for every command below is
`51e02b6b61b314c99740883fb4bee7ce7b9be76b`.

### Phase 40.1's presence inside the range (D-11 requirement)

Phase 40.1's three fix commits, cross-checked against `40.1-NONREGRESSION.md` §4 and §6 (the
GREEN-commit table):

```
$ git rev-parse e8d4f42 9928f93 41d2683
e8d4f4200988808cf1d0948511ed7f57a5a50945
9928f9370fd5cb6ca98310d701f085061913cb2b
41d268331521586078da3c3557654b5638355dfb

$ git merge-base --is-ancestor e8d4f42 aa9d2f06ad854f6f96d285d669ba4bb91b053f31 && echo "e8d4f42 IS in range"
e8d4f42 IS in range

$ git merge-base --is-ancestor 9928f93 aa9d2f06ad854f6f96d285d669ba4bb91b053f31 && echo "9928f93 IS in range"
9928f93 IS in range

$ git merge-base --is-ancestor 41d2683 aa9d2f06ad854f6f96d285d669ba4bb91b053f31 && echo "41d2683 IS in range"
41d2683 IS in range

$ git log --oneline 51e02b6b61b314c99740883fb4bee7ce7b9be76b..aa9d2f06ad854f6f96d285d669ba4bb91b053f31 -- typsphinx/translator.py | grep -i "40.1"
41d2683 fix(40.1-03): promote D-14 anchor decision into one shared predicate
9928f93 fix(40.1-02): widen citation run-adjacency skip list for ids-less targets
e8d4f42 fix(40.1-01): fail-closed WR-01 backref filter in visit_citation
```

All three of Phase 40.1's `typsphinx/translator.py` fix commits resolve as ancestors of HEAD, and
`git log`'s own `BASE..HEAD` filter on `translator.py` finds all three by name. Phase 40.1's
translator changes are demonstrated by SHA to be inside the range this sweep measures — not
asserted.

---

## Invariant 1 of 3 — zero new runtime dependencies

### Full `pyproject.toml` diff

```
$ git diff 51e02b6b61b314c99740883fb4bee7ce7b9be76b..HEAD -- pyproject.toml
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

Two hunks in the full diff, and no others exist. First hunk: the version-field move (plan 41-02).
Second hunk: **one line added to the `dev` extra** — this is the finding this task's own
instructions require surfacing rather than absorbing into a bare "identical" verdict (see below).

### `dependencies` array (the runtime array proper), both sides

```
$ git show 51e02b6b61b314c99740883fb4bee7ce7b9be76b:pyproject.toml | sed -n '/^dependencies/,/^\]/p'
dependencies = [
    "sphinx>=9.1,<10",
    "docutils>=0.21,<0.23",
    "typst>=0.15.0,<0.16",
]

$ git show HEAD:pyproject.toml | sed -n '/^dependencies/,/^\]/p'
dependencies = [
    "sphinx>=9.1,<10",
    "docutils>=0.21,<0.23",
    "typst>=0.15.0,<0.16",
]
```

**Byte-identical. Zero new, changed, or removed runtime dependencies.**

### Dependency-group / dev-extra declarations, both sides

Three declarations exist in `pyproject.toml` besides the runtime array: `[project.optional-
dependencies].dev`, `[project.optional-dependencies].docs`, and the PEP 735 `[dependency-groups]`
table.

```
$ git show HEAD:pyproject.toml | sed -n '146,149p'
[dependency-groups]
dev = [
    "types-docutils>=0.22.2.20251006",
]
```

```
$ git diff 51e02b6b61b314c99740883fb4bee7ce7b9be76b..HEAD -- pyproject.toml | grep -A20 "dependency-groups"
(no output)
```

`[dependency-groups]` is byte-identical between base and HEAD — no diff hunk touches it.

`[project.optional-dependencies].docs` (`furo`, `sphinx-autodoc-typehints`, `sphinx-intl`) is also
unchanged (not present in either diff hunk above).

**`[project.optional-dependencies].dev` is NOT byte-identical** — it gained one line:
`"pillow>=12.3,<13",  # D-07: ADM-04 greyscale render (Image.convert), dev-only`.

```
$ git log --oneline --all | grep -i "pillow"
a5be0b9 feat(39-04): add pillow to dev extra for ADM-04 greyscale render
```

**Finding (reported per this task's own instruction, not absorbed into the verdict below):** this
addition landed in Phase 39 (commit `a5be0b9`, "D-07: ADM-04 greyscale render") — well before this
plan — and is a **dev-only** tooling dependency (Pillow's `Image.convert` for the greyscale
render-comparison script), not a runtime dependency of the shipped `typsphinx` package. It does not
appear in `dependencies`, in `[project.optional-dependencies].docs`, or in `[dependency-groups]`.
The CHANGELOG's own claim 1 ("Zero new runtime dependencies across the full milestone diff") is
worded specifically about *runtime* dependencies, and this addition is outside that scope by
construction — it does not contradict claim 1. It is recorded here in the interest of the
transparency prohibition this plan carries (a finding must be reported, not smoothed over), and
because the plan's `must_haves.truths` names "dependency groups" explicitly as part of what
Invariant 1 measures.

### Verdict — Invariant 1

**PARTIAL, with the deviation fully explained and non-breaching.** The runtime `dependencies` array
and the PEP 735 `[dependency-groups]` table are byte-identical across the milestone (zero new
runtime dependencies — the invariant the CHANGELOG's claim 1 and ROADMAP SC#4 actually assert). The
`dev` extra (a non-runtime, non-`dependency-groups` declaration) gained one dev-only tooling
package, `pillow`, in Phase 39 for the ADM-04 greyscale-comparison script — a pre-existing fact
carried into this measurement, not something introduced by this plan, and not a runtime-dependency
breach. This is reported explicitly rather than folded silently into "identical."

### `uv.lock` diff — third-party version movement check

```
$ git diff --stat 51e02b6b61b314c99740883fb4bee7ce7b9be76b..HEAD -- uv.lock
 uv.lock | 75 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-
 1 file changed, 74 insertions(+), 1 deletion(-)
```

```
$ git diff 51e02b6b61b314c99740883fb4bee7ce7b9be76b..HEAD -- uv.lock | grep -E '^[+-]name = |^[+-]version = '
+name = "pillow"
+version = "12.3.0"
... (74 lines of pillow wheel/sdist entries, elided — see full diff for the complete package block)
-version = "0.6.5"
+version = "0.7.0"
```

The only `name =` line added is `pillow` (the new lock entry for the dev-extra addition just
discussed); the only `version =` lines that changed belong to `typsphinx` itself (the version bump).
**No existing third-party package's pinned version moved anywhere in `uv.lock`.**

Cross-referenced against plan 41-02's own SUMMARY (`41-02-SUMMARY.md`): "`uv.lock` regenerated via
`uv lock` (never hand-edited); diff inspected before commit and confirmed only the typsphinx
package's own version field moved — no third-party dependency drift." That statement was scoped to
41-02's own before/after diff (the version-bump commit alone); this measurement is scoped to the
**full milestone range** and finds the same "no third-party drift" result, plus the pre-existing
Phase 39 `pillow` addition that predates plan 41-02 and is therefore invisible to that plan's own
narrower diff. No contradiction — the two measurements have different scopes and both hold.

---

## Invariant 2 of 3 — the `@preview` surface

### Every `@preview` hit, current tree (HEAD), all three sync sites

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

(`template_engine.py:225` is a docstring example illustrating the `typst_package` config option's
format — `@preview/charged-ieee:0.1.0` is not one of the four bundled packages and is not a real
import statement; it is prose, not a sync site.)

### Same grep against `BASE`

```
$ git show 51e02b6b61b314c99740883fb4bee7ce7b9be76b:typsphinx/writer.py | grep -n "@preview"
155:            imports.append('#import "@preview/codly:1.3.0": *')
156:            imports.append('#import "@preview/codly-languages:0.1.10": *')
157:            imports.append('#import "@preview/mitex:0.2.7": mi, mitex')
158:            imports.append('#import "@preview/gentle-clues:1.3.1": *')

$ git show 51e02b6b61b314c99740883fb4bee7ce7b9be76b:typsphinx/template_engine.py | grep -n "@preview"
225:            typst_package: Typst Universe package specification (e.g., "@preview/charged-ieee:0.1.0")
612:            output_parts.append('#import "@preview/codly:1.3.0": *')
613:            output_parts.append('#import "@preview/codly-languages:0.1.10": *')
614:            output_parts.append('#import "@preview/mitex:0.2.7": mi, mitex')
615:            output_parts.append('#import "@preview/gentle-clues:1.3.1": *')

$ git show 51e02b6b61b314c99740883fb4bee7ce7b9be76b:typsphinx/templates/base.typ | grep -n "@preview"
8:#import "@preview/codly:1.3.0": *
9:#import "@preview/codly-languages:0.1.10": *
14:#import "@preview/mitex:0.2.7": *
19:#import "@preview/gentle-clues:1.3.1": *
```

**Line-for-line identical to HEAD on all three files** (same line numbers, same versions). The four
package pins — `codly:1.3.0`, `codly-languages:0.1.10`, `mitex:0.2.7`, `gentle-clues:1.3.1` — are
the same four names and the same four version strings on both sides of the range.

### Newly added files that declare a `@preview` import

```
$ git diff --diff-filter=A --name-only 51e02b6b61b314c99740883fb4bee7ce7b9be76b..HEAD | xargs grep -l "@preview" 2>/dev/null | grep -v "^\.planning/"
tests/fixtures/admonition_greyscale_probe/_templates/minimal.typ
tests/fixtures/admonition_greyscale_probe/conf.py
tests/fixtures/admonition_locale_title_gate/en/conf.py
tests/fixtures/admonition_locale_title_gate/ja/conf.py
tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
tests/test_citation_degradation_gate.py
```

(A much larger set of `.planning/**/*.md` files also match — these are phase planning prose
discussing the `@preview` hazard by name, not code, and are excluded from this table; they carry no
import statements.)

Per-file classification (content inspected, not the bare filename):

| File | Content at the matched line | Classification |
|---|---|---|
| `tests/fixtures/admonition_greyscale_probe/_templates/minimal.typ` | Real `#import "@preview/...:"` statements for all four packages, same versions as `base.typ` | **Fixture-mirror** — a test template re-declaring the same import block, expected per `test_preview_version_sync.py`'s own docstring precedent |
| `tests/fixtures/admonition_greyscale_probe/conf.py` | Comment prose: `# writer emits the full template plus the gentle-clues @preview import --` | Not an import site at all — a comment mentioning the hazard by name |
| `tests/fixtures/admonition_locale_title_gate/en/conf.py` | Comment prose: `# template plus the gentle-clues @preview wildcard import (see ...)` | Not an import site — comment |
| `tests/fixtures/admonition_locale_title_gate/ja/conf.py` | Comment prose: `# gentle-clues @preview wildcard import.` | Not an import site — comment |
| `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ` | Real `#import "@preview/...:"` statements for all four packages, same versions as `base.typ` | **Fixture-mirror** — a golden `.typ` file mirroring the canonical import block, expected |
| `tests/test_citation_degradation_gate.py` | Comment prose: ``` ``@preview`` imports are needed here -- citation output uses no ``` | Not an import site — comment explaining why citation fixtures need no imports |

**No file under `typsphinx/` or `examples/` appears in this newly-added list — no new production
sync site was introduced this milestone.** The two genuine fixture-mirror files both pin the
identical four versions `base.typ` pins; neither is stale.

```
$ uv run pytest tests/test_preview_version_sync.py -v
tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 33%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 66%]
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED [100%]
============================== 3 passed in 0.02s ===============================
```

### Carried-forward Warning (not a new finding)

`docs/source/_typst/custom_template.typ` remains a pre-existing **fourth** `@preview`
version-lockstep site outside `tests/test_preview_version_sync.py`'s three-site identity check
(the test's own drift-guard extends to `examples/**/*.typ`, not `docs/`) — carried since Phase
30.1's review and reconfirmed unchanged this milestone by the `docs/` diff-stat below:

```
$ git diff --stat 51e02b6b61b314c99740883fb4bee7ce7b9be76b..HEAD -- docs/
(no output)
```

Zero lines changed under `docs/` this milestone. The fourth site is therefore unchanged and out of
this phase's scope per `41-CONTEXT.md`'s "no change under `docs/`" rule — reported here as a
Warning already on record, not as something this sweep discovered.

### Verdict — Invariant 2

**PROVEN.** All three declaration sites (`writer.py`, `template_engine.py`, `templates/base.typ`)
are line-for-line identical between BASE and HEAD; the four package names and version strings agree
on both sides; no newly added file under `typsphinx/` or `examples/` introduces a new production
`@preview` import site; the two genuine test-fixture mirrors that do carry real import statements
both pin the current canonical versions; `test_preview_version_sync.py`'s three assertions pass.

---

## Cross-check — CHANGELOG `### Verified` claims 1 and 2

Quoted verbatim from `CHANGELOG.md`'s `## [0.7.0] - 2026-08-03` entry:

> - Zero new runtime dependencies across the full milestone diff.
> - The four bundled `@preview` package version strings unchanged across all four sync surfaces
>   (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`).

**Claim 1 — "Zero new runtime dependencies across the full milestone diff." HOLDS.** Invariant 1's
measurement shows the runtime `dependencies` array is byte-identical across the full range. The
claim is worded specifically about *runtime* dependencies, and the one dev-extra addition found
(`pillow`, Phase 39, D-07) is outside that scope by construction — it does not weaken this claim.
(Note: claim 1's own wording is precise enough that it does not need amendment even though a
dev-only dependency was in fact added somewhere in the diff — a reader parsing "runtime
dependencies" literally is not misled.)

**Claim 2 — "The four bundled `@preview` package version strings unchanged across all four sync
surfaces (`writer.py` / `template_engine.py` / `templates/base.typ` / `examples/**/*.typ`)." HOLDS.**
Invariant 2's measurement confirms all three code-level declaration sites are byte-identical and
`test_example_templates_match_canonical_versions` (the fourth surface, `examples/**/*.typ`) passes,
confirming no example under `examples/` pins a stale version of any of the four packages. Note the
CHANGELOG's own wording here counts "four sync surfaces" (three identity-locked declaration sites
plus the `examples/**/*.typ` drift-guard), which is a different "four" than "four package pins" —
both numbers happen to be four in this milestone, and the claim is worded correctly for what
`test_preview_version_sync.py` actually enforces (verified by reading that test's own docstring and
three test functions above), not a coincidental overlap that a naive re-reading might flag as
ambiguous.

**No divergence found.** Both claims hold as measured against this session's re-run, and no
CHANGELOG edit is warranted or made by this plan (which does not edit `CHANGELOG.md`).

---

## Invariant 3 of 3 — every node-handler change carries a recorded-RED GATE-01 fixture

### The census method

Implemented as a scratch script under `/tmp` (never committed — confirmed at the end of this
section), following `41-RESEARCH.md`'s hunk-boundary + function-start-line attribution method
verbatim: read `typsphinx/translator.py` at both `BASE` and `HEAD` via `git show`, build an ordered
`(line_number, function_name)` list on each side from `def <name>(` lines, walk
`git diff -U0 BASE..HEAD -- typsphinx/translator.py`, and attribute every removed line to the
enclosing function on the BASE side and every added line to the enclosing function on the HEAD
side. The union, filtered to names starting `visit_` or `depart_`, is the census.

### Census output (re-derived this session, BASE=`51e02b6`, HEAD=`aa9d2f0`)

```
$ uv run python /tmp/.../census.py
COUNT=51
```

**51 handlers touched**, full sorted list:

`depart_citation`, `depart_desc`, `depart_desc_content`, `depart_desc_name`,
`depart_desc_optional`, `depart_desc_parameter`, `depart_desc_parameterlist`,
`depart_desc_sig_name`, `depart_desc_signature`, `depart_field`, `depart_field_body`,
`depart_field_list`, `depart_field_name`, `depart_literal_emphasis`, `depart_literal_strong`,
`depart_paragraph`, `depart_reference`, `depart_rubric`, `visit_Text`, `visit_admonition`,
`visit_attention`, `visit_citation`, `visit_danger`, `visit_desc_addname`,
`visit_desc_annotation`, `visit_desc_content`, `visit_desc_name`, `visit_desc_optional`,
`visit_desc_parameter`, `visit_desc_parameterlist`, `visit_desc_returns`,
`visit_desc_sig_keyword`, `visit_desc_sig_name`, `visit_desc_sig_operator`,
`visit_desc_sig_punctuation`, `visit_desc_sig_space`, `visit_desc_signature`,
`visit_field_body`, `visit_field_list`, `visit_field_name`, `visit_hint`, `visit_important`,
`visit_label`, `visit_literal_emphasis`, `visit_literal_strong`, `visit_math_block`,
`visit_paragraph`, `visit_reference`, `visit_rubric`, `visit_seealso`, `visit_topic`.

**Brand-new on the HEAD side** (present in HEAD's function list, absent from BASE's — i.e. the
handler did not exist at all at the milestone base): `depart_citation`, `visit_citation`,
`visit_label`. All three are Phase 40's greenfield citation handlers (CIT-01..CIT-06) — zero
citation handlers existed at `v0.6.5-1-g51e02b6`.

**Non-handler methods the same census touched** (context for the scope statement — these are
helper/private methods whose diff hunks fall inside them, not `visit_`/`depart_` handlers, so they
are outside SC#4's own "node-handler change" wording but recorded here per the plan's "record the
non-handler methods... as context" instruction): `__init__`, `_citation_run_neighbour`,
`_depart_admonition`, `_emit_field_body_monospace_leaf`, `_emit_signature_leaf_wrapper`,
`_escape_signature_text`, `_exit_inline_concat_element`, `_find_citing_reference`,
`_reference_anchor_decision`, `_visit_admonition`.

### Cross-check against `41-RESEARCH.md`'s recorded 51

**Delta: zero handlers differ — the count is 51 and the sorted name list is byte-for-byte
identical to `41-RESEARCH.md`'s "Code Examples" list**, despite the range's tip moving from the
research session's measurement point (369 commits past BASE at the time) to this session's 394. A
programmatic set-difference (both directions) over the two 51-name lists returns empty in both
directions.

**This is explained, not merely reported as a bare "0":**

- **This phase's own D-12 commit** (`c81ca29`, "escape the unbalanced asterisk in
  `visit_desc_sig_name`'s docstring") touches `typsphinx/translator.py` inside the body of
  `visit_desc_sig_name` — but `visit_desc_sig_name` **already appears** in the research session's
  51-name list (it carries real Phase 37-era SIG behavioural changes independent of this
  docstring). D-12's edit therefore adds diff *lines* inside an already-touched function; it adds
  no *new* handler name to the union, so the census count and name set are unaffected by it. (Step
  3 below reproduces this specific commit's diff to confirm it is docstring-only.)
- **Every other commit landed since the research session's measurement** (this phase's own
  planning-record commits, the CHANGELOG/version-bump commits, this plan's own Task 1 commit, and
  Phase 40.1's housekeeping) either does not touch `typsphinx/translator.py` at all, or — where it
  does (D-12, above) — lands inside a function already in the union. No commit since the research
  session introduced a new touched handler.
- The three Phase 40.1 fix commits (`e8d4f42`, `9928f93`, `41d2683`) were **already inside the
  range at the research session's own measurement time** (Phase 40.1 had already landed before
  Phase 41's research session ran, per `41-CONTEXT.md`'s own execution-order note) — so their
  contribution to the census (the `_citation_run_neighbour`, `_reference_anchor_decision`,
  `_find_citing_reference` non-handler entries, and no new `visit_`/`depart_` name since WR-01/02/03
  only edit already-touched citation-family handlers/helpers) was already reflected in the
  research session's 51, not newly discovered here.

### The coverage map (node-name grep, per Pitfall 4)

Method: for each of the 51 censused handlers, strip the leading `visit_`/`depart_` prefix to get
the **node name**, then `grep -l <node> tests/*.py` (top-level test modules only — not
`tests/fixtures/**`, which are fixture data, not gate assertions) to find every covering gate
module. Searching for the literal *method* name (`visit_desc_addname` etc., prefix included) was
verified first to reproduce Pitfall 4's false-negative: e.g. `grep -l visit_desc_addname
tests/*.py` returns **zero** hits, while `grep -l desc_addname tests/*.py` returns four — gate
modules describe the docutils/Sphinx *node*, never the Python visitor method with its
`visit_`/`depart_` prefix.

| Handler | Node name | Match count | Covering gate module(s) |
|---|---|---|---|
| `depart_citation` | `citation` | 5 | `test_citation_degradation_gate.py`, `test_citation_render_gate.py`, `test_corpus_gate.py`, `test_desc_break_marker_buffer_swap_gate.py`, `test_pdf_render_gate.py` |
| `depart_desc` | `desc` | 29 | `test_admonition_greyscale_pipeline.py`, `test_citation_render_gate.py`, `test_confval_field_spacing_render_gate.py`, `test_corpus_gate.py`, `test_deflist_nested_definition_render_gate.py`, `test_deflist_term_concat_render_gate.py`, `test_deflist_term_inline_children_gate.py`, `test_desc_bodyless_concat_render_gate.py`, `test_desc_break_marker_buffer_swap_gate.py`, `test_desc_container_propagated_target_render_gate.py`, `test_desc_content_indent_render_gate.py`, `test_desc_rubric_decoupling_render_gate.py`, `test_desc_sig_space_render_gate.py`, `test_desc_signature_anchor_render_gate.py`, `test_desc_signature_concat_render_gate.py`, `test_examples_charged_ieee_gate.py`, `test_field_body_typography_render_gate.py`, `test_nested_master_render_gate.py`, `test_pdf_render_gate.py`, `test_rubric_indent_invariance.py`, `test_rubric_option_concat_render_gate.py`, `test_rubric_strong_nesting_render_gate.py`, `test_signature_break_and_arrow_gate.py`, `test_signature_overflow_render_gate.py`, `test_signature_page_boundary_render_gate.py`, `test_signature_typography_gate.py`, `test_signature_typography_multi_signature_page_count_gate.py`, `test_substitution_definition_render_gate.py`, `test_translator.py` |
| `depart_desc_content` | `desc_content` | 7 | `test_citation_render_gate.py`, `test_desc_content_indent_render_gate.py`, `test_field_body_typography_render_gate.py`, `test_rubric_indent_invariance.py`, `test_signature_break_and_arrow_gate.py`, `test_signature_page_boundary_render_gate.py`, `test_translator.py` |
| `depart_desc_name` | `desc_name` | 6 | `test_desc_sig_space_render_gate.py`, `test_desc_signature_concat_render_gate.py`, `test_rubric_option_concat_render_gate.py`, `test_signature_overflow_render_gate.py`, `test_signature_typography_gate.py`, `test_translator.py` |
| `depart_desc_optional` | `desc_optional` | 3 | `test_pdf_render_gate.py`, `test_signature_break_and_arrow_gate.py`, `test_signature_typography_gate.py` |
| `depart_desc_parameter` | `desc_parameter` | 7 | `test_confval_field_spacing_render_gate.py`, `test_deflist_term_concat_render_gate.py`, `test_deflist_term_inline_children_gate.py`, `test_desc_sig_space_render_gate.py`, `test_desc_signature_concat_render_gate.py`, `test_signature_typography_gate.py`, `test_translator.py` |
| `depart_desc_parameterlist` | `desc_parameterlist` | 3 | `test_desc_signature_concat_render_gate.py`, `test_signature_typography_gate.py`, `test_translator.py` |
| `depart_desc_sig_name` | `desc_sig_name` | 4 | `test_desc_sig_space_render_gate.py`, `test_desc_signature_concat_render_gate.py`, `test_signature_typography_gate.py`, `test_translator.py` |
| `depart_desc_signature` | `desc_signature` | 16 | `test_deflist_nested_definition_render_gate.py`, `test_desc_container_propagated_target_render_gate.py`, `test_desc_content_indent_render_gate.py`, `test_desc_rubric_decoupling_render_gate.py`, `test_desc_sig_space_render_gate.py`, `test_desc_signature_anchor_render_gate.py`, `test_desc_signature_concat_render_gate.py`, `test_field_body_typography_render_gate.py`, `test_pdf_render_gate.py`, `test_rubric_option_concat_render_gate.py`, `test_rubric_strong_nesting_render_gate.py`, `test_signature_overflow_render_gate.py`, `test_signature_page_boundary_render_gate.py`, `test_signature_typography_gate.py`, `test_signature_typography_multi_signature_page_count_gate.py`, `test_translator.py` |
| `depart_field` | `field` | 18 | `test_citation_render_gate.py`, `test_confval_field_body_render_gate.py`, `test_confval_field_spacing_render_gate.py`, `test_cross_doc_label_namespace_render_gate.py`, `test_desc_bodyless_concat_render_gate.py`, `test_desc_content_indent_render_gate.py`, `test_desc_rubric_decoupling_render_gate.py`, `test_field_body_typography_render_gate.py`, `test_field_list_in_list_item_render_gate.py`, `test_inline_math_after_text_render_gate.py`, `test_package_only_config_gate.py`, `test_readme_version_sync.py`, `test_rubric_option_concat_render_gate.py`, `test_signature_break_and_arrow_gate.py`, `test_signature_page_boundary_render_gate.py`, `test_signature_typography_multi_signature_page_count_gate.py`, `test_table_in_list_item_render_gate.py`, `test_translator.py` |
| `depart_field_body` | `field_body` | 6 | `test_citation_render_gate.py`, `test_confval_field_body_render_gate.py`, `test_desc_content_indent_render_gate.py`, `test_field_body_typography_render_gate.py`, `test_field_list_in_list_item_render_gate.py`, `test_translator.py` |
| `depart_field_list` | `field_list` | 7 | `test_citation_render_gate.py`, `test_desc_content_indent_render_gate.py`, `test_field_body_typography_render_gate.py`, `test_field_list_in_list_item_render_gate.py`, `test_signature_page_boundary_render_gate.py`, `test_table_in_list_item_render_gate.py`, `test_translator.py` |
| `depart_field_name` | `field_name` | 4 | `test_confval_field_spacing_render_gate.py`, `test_field_body_typography_render_gate.py`, `test_field_list_in_list_item_render_gate.py`, `test_translator.py` |
| `depart_literal_emphasis` | `literal_emphasis` | 2 | `test_desc_rubric_decoupling_render_gate.py`, `test_field_body_typography_render_gate.py` |
| `depart_literal_strong` | `literal_strong` | 2 | `test_desc_rubric_decoupling_render_gate.py`, `test_field_body_typography_render_gate.py` |
| `depart_paragraph` | `paragraph` | 34 | `conftest.py`, `test_admonitions.py`, `test_changelog_extraction.py`, `test_citation_degradation_gate.py`, `test_citation_render_gate.py`, `test_confval_field_body_render_gate.py`, `test_corpus_gate.py`, `test_deflist_definition_multiblock_render_gate.py`, `test_deflist_nested_definition_render_gate.py`, `test_desc_bodyless_concat_render_gate.py`, `test_desc_content_indent_render_gate.py`, `test_desc_rubric_decoupling_render_gate.py`, `test_desc_sig_space_render_gate.py`, `test_field_body_typography_render_gate.py`, `test_field_list_in_list_item_render_gate.py`, `test_footnotes.py`, `test_inline_math_after_text_render_gate.py`, `test_inline_references.py`, `test_list_item_nested_block_render_gate.py`, `test_package_only_config_gate.py`, `test_paragraph_concat_render_gate.py`, `test_paragraph_propagated_target_render_gate.py`, `test_paragraph_soft_newline_render_gate.py`, `test_pdf_render_gate.py`, `test_ref_target_nested_list_render_gate.py`, `test_rubric_indent_invariance.py`, `test_rubric_strong_nesting_render_gate.py`, `test_signature_break_and_arrow_gate.py`, `test_signature_page_boundary_render_gate.py`, `test_signature_typography_multi_signature_page_count_gate.py`, `test_target_label_render_gate.py`, `test_topics.py`, `test_translator.py`, `test_wide_table_render_gate.py` |
| `depart_reference` | `reference` | 41 | `test_builder_requirement13.py`, `test_citation_degradation_gate.py`, `test_citation_render_gate.py`, `test_corpus_gate.py`, `test_cross_doc_label_namespace_render_gate.py`, `test_deflist_nested_definition_render_gate.py`, `test_deflist_term_inline_children_gate.py`, `test_desc_container_propagated_target_render_gate.py`, `test_desc_sig_space_render_gate.py`, `test_desc_signature_anchor_render_gate.py`, `test_desc_signature_concat_render_gate.py`, `test_duplicate_include_label_render_gate.py`, `test_examples_charged_ieee_gate.py`, `test_external_link_style_render_gate.py`, `test_field_body_typography_render_gate.py`, `test_footnotes.py`, `test_glob_image_render_gate.py`, `test_inline_references.py`, `test_integration_nested_toctree.py`, `test_label_at_char_render_gate.py`, `test_nested_master_render_gate.py`, `test_nested_toctree_paths.py`, `test_no_stale_github_io_links.py`, `test_package_only_config_gate.py`, `test_package_template_routing.py`, `test_paragraph_propagated_target_render_gate.py`, `test_pdf_render_gate.py`, `test_readthedocs_config.py`, `test_ref_target_nested_list_render_gate.py`, `test_rubric_indent_invariance.py`, `test_rubric_propagated_target_render_gate.py`, `test_signature_typography_gate.py`, `test_static_asset_copy_gate.py`, `test_substitution_definition_render_gate.py`, `test_target_label_render_gate.py`, `test_template_assets.py`, `test_template_engine.py`, `test_template_import_path.py`, `test_topics.py`, `test_translator.py`, `test_xref_orphan_degrade_render_gate.py` |
| `depart_rubric` | `rubric` | 11 | `test_admonition_bucket_render_gate.py`, `test_admonition_greyscale_pipeline.py`, `test_admonition_locale_title_precedence_gate.py`, `test_citation_render_gate.py`, `test_desc_rubric_decoupling_render_gate.py`, `test_rubric_indent_invariance.py`, `test_rubric_option_concat_render_gate.py`, `test_rubric_propagated_target_render_gate.py`, `test_rubric_strong_nesting_render_gate.py`, `test_signature_typography_multi_signature_page_count_gate.py`, `test_translator.py` |
| `visit_Text` | `Text` | 22 | `test_admonitions.py`, `test_builder_requirement13.py`, `test_citation_degradation_gate.py`, `test_confval_field_body_render_gate.py`, `test_deflist_term_concat_render_gate.py`, `test_deflist_term_inline_children_gate.py`, `test_desc_sig_space_render_gate.py`, `test_epigraph_render_gate.py`, `test_examples_basic.py`, `test_footnotes.py`, `test_inline_math_after_text_render_gate.py`, `test_inline_references.py`, `test_line_blocks.py`, `test_math_mitex.py`, `test_paragraph_soft_newline_render_gate.py`, `test_rubric_strong_nesting_render_gate.py`, `test_signature_typography_gate.py`, `test_table_in_list_item_render_gate.py`, `test_topics.py`, `test_translator.py`, `test_typst_string_escape_gate.py`, `test_xref_orphan_degrade_render_gate.py` |
| `visit_admonition` | `admonition` | 11 | `test_admonition_bucket_render_gate.py`, `test_admonition_greyscale_pipeline.py`, `test_admonition_locale_title_precedence_gate.py`, `test_admonitions.py`, `test_citation_render_gate.py`, `test_desc_break_marker_buffer_swap_gate.py`, `test_line_blocks.py`, `test_paragraph_propagated_target_render_gate.py`, `test_pdf_render_gate.py`, `test_preview_smoke_gate.py`, `test_topics.py` |
| `visit_attention` | `attention` | 4 | `test_admonition_bucket_render_gate.py`, `test_admonition_locale_title_precedence_gate.py`, `test_admonitions.py`, `test_pdf_render_gate.py` |
| `visit_citation` | `citation` | 5 | `test_citation_degradation_gate.py`, `test_citation_render_gate.py`, `test_corpus_gate.py`, `test_desc_break_marker_buffer_swap_gate.py`, `test_pdf_render_gate.py` |
| `visit_danger` | `danger` | 4 | `test_admonition_bucket_render_gate.py`, `test_admonition_locale_title_precedence_gate.py`, `test_admonitions.py`, `test_pdf_render_gate.py` |
| `visit_desc_addname` | `desc_addname` | 4 | `test_desc_sig_space_render_gate.py`, `test_rubric_option_concat_render_gate.py`, `test_signature_overflow_render_gate.py`, `test_signature_typography_gate.py` |
| `visit_desc_annotation` | `desc_annotation` | 3 | `test_desc_sig_space_render_gate.py`, `test_signature_typography_gate.py`, `test_translator.py` |
| `visit_desc_content` | `desc_content` | 7 | `test_citation_render_gate.py`, `test_desc_content_indent_render_gate.py`, `test_field_body_typography_render_gate.py`, `test_rubric_indent_invariance.py`, `test_signature_break_and_arrow_gate.py`, `test_signature_page_boundary_render_gate.py`, `test_translator.py` |
| `visit_desc_name` | `desc_name` | 6 | `test_desc_sig_space_render_gate.py`, `test_desc_signature_concat_render_gate.py`, `test_rubric_option_concat_render_gate.py`, `test_signature_overflow_render_gate.py`, `test_signature_typography_gate.py`, `test_translator.py` |
| `visit_desc_optional` | `desc_optional` | 3 | `test_pdf_render_gate.py`, `test_signature_break_and_arrow_gate.py`, `test_signature_typography_gate.py` |
| `visit_desc_parameter` | `desc_parameter` | 7 | `test_confval_field_spacing_render_gate.py`, `test_deflist_term_concat_render_gate.py`, `test_deflist_term_inline_children_gate.py`, `test_desc_sig_space_render_gate.py`, `test_desc_signature_concat_render_gate.py`, `test_signature_typography_gate.py`, `test_translator.py` |
| `visit_desc_parameterlist` | `desc_parameterlist` | 3 | `test_desc_signature_concat_render_gate.py`, `test_signature_typography_gate.py`, `test_translator.py` |
| `visit_desc_returns` | `desc_returns` | 2 | `test_pdf_render_gate.py`, `test_signature_break_and_arrow_gate.py` |
| `visit_desc_sig_keyword` | `desc_sig_keyword` | **1** | `test_desc_sig_space_render_gate.py` |
| `visit_desc_sig_name` | `desc_sig_name` | 4 | `test_desc_sig_space_render_gate.py`, `test_desc_signature_concat_render_gate.py`, `test_signature_typography_gate.py`, `test_translator.py` |
| `visit_desc_sig_operator` | `desc_sig_operator` | 2 | `test_desc_sig_space_render_gate.py`, `test_signature_typography_gate.py` |
| `visit_desc_sig_punctuation` | `desc_sig_punctuation` | **1** | `test_desc_sig_space_render_gate.py` |
| `visit_desc_sig_space` | `desc_sig_space` | **1** | `test_desc_sig_space_render_gate.py` |
| `visit_desc_signature` | `desc_signature` | 16 | `test_deflist_nested_definition_render_gate.py`, `test_desc_container_propagated_target_render_gate.py`, `test_desc_content_indent_render_gate.py`, `test_desc_rubric_decoupling_render_gate.py`, `test_desc_sig_space_render_gate.py`, `test_desc_signature_anchor_render_gate.py`, `test_desc_signature_concat_render_gate.py`, `test_field_body_typography_render_gate.py`, `test_pdf_render_gate.py`, `test_rubric_option_concat_render_gate.py`, `test_rubric_strong_nesting_render_gate.py`, `test_signature_overflow_render_gate.py`, `test_signature_page_boundary_render_gate.py`, `test_signature_typography_gate.py`, `test_signature_typography_multi_signature_page_count_gate.py`, `test_translator.py` |
| `visit_field_body` | `field_body` | 6 | `test_citation_render_gate.py`, `test_confval_field_body_render_gate.py`, `test_desc_content_indent_render_gate.py`, `test_field_body_typography_render_gate.py`, `test_field_list_in_list_item_render_gate.py`, `test_translator.py` |
| `visit_field_list` | `field_list` | 7 | `test_citation_render_gate.py`, `test_desc_content_indent_render_gate.py`, `test_field_body_typography_render_gate.py`, `test_field_list_in_list_item_render_gate.py`, `test_signature_page_boundary_render_gate.py`, `test_table_in_list_item_render_gate.py`, `test_translator.py` |
| `visit_field_name` | `field_name` | 4 | `test_confval_field_spacing_render_gate.py`, `test_field_body_typography_render_gate.py`, `test_field_list_in_list_item_render_gate.py`, `test_translator.py` |
| `visit_hint` | `hint` | 3 | `test_admonition_bucket_render_gate.py`, `test_admonitions.py`, `test_pdf_render_gate.py` |
| `visit_important` | `important` | 2 | `test_admonition_bucket_render_gate.py`, `test_admonitions.py` |
| `visit_label` | `label` | 40 | `test_admonition_bucket_render_gate.py`, `test_admonition_locale_title_precedence_gate.py`, `test_admonitions.py`, `test_citation_degradation_gate.py`, `test_citation_render_gate.py`, `test_confval_field_body_render_gate.py`, `test_corpus_gate.py`, `test_cross_doc_label_namespace_render_gate.py`, `test_deflist_definition_multiblock_render_gate.py`, `test_deflist_nested_definition_render_gate.py`, `test_deflist_term_concat_render_gate.py`, `test_desc_container_propagated_target_render_gate.py`, `test_desc_rubric_decoupling_render_gate.py`, `test_desc_signature_anchor_render_gate.py`, `test_duplicate_include_label_render_gate.py`, `test_external_link_style_render_gate.py`, `test_field_body_typography_render_gate.py`, `test_field_list_in_list_item_render_gate.py`, `test_footnotes.py`, `test_inline_math_after_text_render_gate.py`, `test_inline_references.py`, `test_label_at_char_render_gate.py`, `test_list_item_nested_block_render_gate.py`, `test_math_fallback.py`, `test_math_mitex.py`, `test_math_native.py`, `test_paragraph_propagated_target_render_gate.py`, `test_pdf_render_gate.py`, `test_ref_target_nested_list_render_gate.py`, `test_rubric_propagated_target_render_gate.py`, `test_signature_overflow_render_gate.py`, `test_signature_typography_gate.py`, `test_substitution_definition_render_gate.py`, `test_target_label_render_gate.py`, `test_template_import_path.py`, `test_topics.py`, `test_typst_lang_gate.py`, `test_typst_string_escape_gate.py`, `test_xref_orphan_degrade_render_gate.py` |
| `visit_literal_emphasis` | `literal_emphasis` | 2 | `test_desc_rubric_decoupling_render_gate.py`, `test_field_body_typography_render_gate.py` |
| `visit_literal_strong` | `literal_strong` | 2 | `test_desc_rubric_decoupling_render_gate.py`, `test_field_body_typography_render_gate.py` |
| `visit_math_block` | `math_block` | 5 | `test_inline_math_after_text_render_gate.py`, `test_math_fallback.py`, `test_math_mitex.py`, `test_math_native.py`, `test_rubric_propagated_target_render_gate.py` |
| `visit_paragraph` | `paragraph` | 34 | (same 34 modules as `depart_paragraph` above) |
| `visit_reference` | `reference` | 41 | (same 41 modules as `depart_reference` above) |
| `visit_rubric` | `rubric` | 11 | (same 11 modules as `depart_rubric` above) |
| `visit_seealso` | `seealso` | 3 | `test_admonition_bucket_render_gate.py`, `test_admonitions.py`, `test_pdf_render_gate.py` |
| `visit_topic` | `topic` | 8 | `test_admonition_bucket_render_gate.py`, `test_cross_doc_label_namespace_render_gate.py`, `test_footnotes.py`, `test_pdf_render_gate.py`, `test_rubric_propagated_target_render_gate.py`, `test_signature_overflow_render_gate.py`, `test_signature_page_boundary_render_gate.py`, `test_topics.py` |

**Zero handlers have zero matches** — all 51 map to at least one gate module by this method,
confirming `41-RESEARCH.md`'s Pitfall 4 finding: the apparent gap the literal-method-name search
produces is a search-method false negative, not a real coverage gap.

**Three handlers are single-hit**: `visit_desc_sig_keyword`, `visit_desc_sig_punctuation`, and
`visit_desc_sig_space` — all three map only to `tests/test_desc_sig_space_render_gate.py`. These
are the exact handlers `41-RESEARCH.md`'s Open Question 2 named as the likeliest false-positive
family (trivial-looking signature pass-through handlers) and are the subject of Task 3's spot-check.

### What this map does and does not establish

**This map shows that the node type's name appears somewhere in the listed gate module(s) — that
is necessary but NOT sufficient proof of coverage.** A grep hit only confirms the module mentions
the node by name (in an assertion, a fixture path, a docstring, or a comment); it does not by
itself prove that module's assertions actually exercise this milestone's specific diff hunks for
that handler. A module could, in principle, mention a node name only in prose explaining what the
node used to render as, without asserting anything about its current behaviour — that would be a
false-positive coverage claim this map alone cannot distinguish from real coverage. Task 3 responds
to this limitation directly by reading each single-hit module's actual `assert` statements rather
than accepting the grep hit as proof.

### Scratch tooling confirmation

```
$ git status --porcelain -- typsphinx tests scripts
(no output)
```

Both scratch scripts (`census.py`, `coverage_map.py`) live under `/tmp/claude-1000/...` — outside
the repository entirely — and were never `git add`ed. No new file appears anywhere under
`typsphinx/`, `tests/`, or `scripts/`.

---

## Spot-check — the single-hit mappings

Per Task 2's coverage table, exactly three handlers are single-hit: `visit_desc_sig_keyword`,
`visit_desc_sig_punctuation`, `visit_desc_sig_space` — all three map only to
`tests/test_desc_sig_space_render_gate.py`. Each is verified below against that module's actual
assertions and against the real doctree the module's own fixture produces, not accepted on the grep
hit alone.

**Method:** built and inspected the fixture's real doctree (`sphinx-build -b typstpdf
tests/fixtures/desc_sig_space_render_gate <scratch>`, then unpickled `.doctrees/index.doctree` and
enumerated every `addnodes.desc_sig_keyword` / `desc_sig_space` / `desc_sig_punctuation` /
`desc_sig_operator` / `desc_sig_name` node with `findall()`), to confirm which node types the
fixture's RST actually produces before crediting the module's `.typ`/PDF assertions to them:

```
$ uv run python /tmp/.../inspect_doctree.py
desc_sig_keyword: count=1 texts=['class']
desc_sig_space: count=6 texts=[' ', ' ', ' ', ' ', ' ', ' ']
desc_sig_punctuation: count=4 texts=['*', '*', '(', ')']
desc_sig_operator: count=1 texts=['*']
desc_sig_name: count=9 texts=['PyObject', 'PyType_GenericAlloc', 'PyTypeObject', 'type', 'Py_ssize_t', 'nitems', 'a', 'f', 'a']
```

The fixture's `.. py:class:: sphinx.builders.html.StandaloneHTMLBuilder` directive produces exactly
one `desc_sig_keyword` node (text `"class"`) immediately followed by a `desc_sig_space` node; the
`.. c:function:: PyObject *PyType_GenericAlloc(...)` directive produces `desc_sig_punctuation` nodes
for the pointer stars (`"*"`) and the parameter-list parens.

| Handler | Module | Assertion(s) quoted | Verdict |
|---|---|---|---|
| `visit_desc_sig_keyword` | `test_desc_sig_space_render_gate.py` | `test_typstpdf_desc_sig_space_produces_pdf_with_structural_spaces`: `assert 'raw("class")\n raw(" ")\n raw("sphinx' in typ_text` (FID-07). The doctree confirms `desc_sig_keyword`'s sole occurrence is the `"class"` text this assertion checks for — `visit_desc_sig_keyword`'s no-op lets this `Text` child stream through `visit_Text`'s monospace branch to produce exactly the quoted `raw("class")`. Also `test_pdf_extracted_text_has_no_merged_tokens`: `assert "class sphinx" in full_text` / `assert "classsphinx" not in full_text`. | **COVERED** |
| `visit_desc_sig_punctuation` | `test_desc_sig_space_render_gate.py` | `test_typstpdf_desc_sig_space_produces_pdf_with_structural_spaces`: `assert 'raw("PyObject")\n raw(" ")\n raw("*")\n strong(raw("PyType_GenericAlloc"))' in typ_text` (FID-08). The doctree confirms the `"*"` (pointer star) between `PyObject` and `PyType_GenericAlloc` is a `desc_sig_punctuation` node — `visit_desc_sig_punctuation`'s no-op lets this `Text` child stream through to the quoted `raw("*")`. | **COVERED** |
| `visit_desc_sig_space` | `test_desc_sig_space_render_gate.py` | Same FID-07 assertion as `visit_desc_sig_keyword` above (`raw(" ")` between `raw("class")` and `raw("sphinx`) plus this module's own docstring naming `visit_desc_sig_space` as the literal shipping bug this fixture was built to catch (the historical `self.body.append(" ")` + `SkipNode` short-circuit that discarded the node's real content-space value). The doctree confirms 6 real `desc_sig_space` nodes exist in this fixture, one of which is the exact FID-07 subject. | **COVERED** |

**No single-hit handler is NOT COVERED.** All three verdicts rest on a quoted assertion tied to a
doctree-confirmed node occurrence, not on the module mentioning the node name in prose — no open
SC#4 gap is recorded from this spot-check.

---

## Phase 40.1 coverage (D-11 fold-in)

Per `41-CONTEXT.md` D-11, this section reproduces `40.1-NONREGRESSION.md` §4's change-site → RED
manifest (written expressly for this sweep) rather than re-deriving it, and confirms each row's
named referents actually resolve in this repository.

| # | Change site | Warning | Evidence file (existence confirmed) | RED commit (resolution confirmed) |
|---|---|---|---|---|
| 1 | `visit_citation`'s backref loop (fail-closed condition) | WR-01 | `40.1-GATE-EVIDENCE-01.md` | `0ebe8c3` |
| 2 | `_citation_run_neighbour` (skip-list widened for ids-less targets) | WR-02 | `40.1-GATE-EVIDENCE-02.md` | `7aa1fe3` |
| 3 | `_ReferenceAnchorDecision` / `_reference_anchor_decision` (new shared predicate) + `visit_reference` rewiring | WR-03 | `40.1-GATE-EVIDENCE-03.md` | `ae9a0fe` |
| 4 | Deletion of `_citing_reference_has_own_anchor` | WR-03 (same evidence file as row 3) | `40.1-GATE-EVIDENCE-03.md` | `ae9a0fe` (shared with row 3) |

```
$ test -f .planning/phases/40.1-citation-degradation-hardening/40.1-GATE-EVIDENCE-01.md && echo "FOUND: 40.1-GATE-EVIDENCE-01.md"
FOUND: 40.1-GATE-EVIDENCE-01.md
$ test -f .planning/phases/40.1-citation-degradation-hardening/40.1-GATE-EVIDENCE-02.md && echo "FOUND: 40.1-GATE-EVIDENCE-02.md"
FOUND: 40.1-GATE-EVIDENCE-02.md
$ test -f .planning/phases/40.1-citation-degradation-hardening/40.1-GATE-EVIDENCE-03.md && echo "FOUND: 40.1-GATE-EVIDENCE-03.md"
FOUND: 40.1-GATE-EVIDENCE-03.md

$ git cat-file -e 0ebe8c3 && echo "0ebe8c3 resolves"
0ebe8c3 resolves
$ git cat-file -e 7aa1fe3 && echo "7aa1fe3 resolves"
7aa1fe3 resolves
$ git cat-file -e ae9a0fe && echo "ae9a0fe resolves"
ae9a0fe resolves
```

All three evidence files exist at their recorded paths; all three RED commit SHAs resolve as real
objects in this repository. The fold-in rests on verified referents, not on `40.1-NONREGRESSION.md`'s
word alone (per the plan's own T-41-25 mitigation).

### Cross-checking the 4 change sites against Task 2's handler census

- **Row 1** (`visit_citation`): present in Task 2's 51-handler census (a `visit_`-prefixed node
  handler). Directly covered.
- **Row 2** (`_citation_run_neighbour`): **absent from the 51-handler list by design** — it is a
  private helper method, not a `visit_`/`depart_` node handler, so it correctly falls outside a
  handler census by name. It IS present in Task 2's separately-recorded "non-handler methods the
  same census touched" list (`_citation_run_neighbour` appears there verbatim). Not a silent gap.
- **Row 3** (`_ReferenceAnchorDecision` / `_reference_anchor_decision`, plus `visit_reference`'s
  rewiring): the new predicate method (`_reference_anchor_decision`) is a private helper, correctly
  absent from the handler list and present in the non-handler list; its caller, `visit_reference`,
  **is** in the 51-handler census (it is a rewired, not newly created, handler — `visit_reference`
  existed at BASE and gets its diff-hunk attribution from being edited to call the new predicate).
  Covered via its caller.
- **Row 4** (deletion of `_citing_reference_has_own_anchor`): **absent from BOTH the handler census
  AND the non-handler-methods list, for a structural reason distinct from rows 2/3** — measured
  directly:

  ```
  $ git show 51e02b6b61b314c99740883fb4bee7ce7b9be76b:typsphinx/translator.py | grep -n "_citing_reference_has_own_anchor"
  (no output)
  $ git show aa9d2f06ad854f6f96d285d669ba4bb91b053f31:typsphinx/translator.py | grep -n "_citing_reference_has_own_anchor"
  (three docstring/comment mentions, no `def` line)
  ```

  `_citing_reference_has_own_anchor` does not exist as a function at either endpoint of the
  `BASE..HEAD` range — it was **both created and deleted entirely inside the range** (created in
  Phase 40, deleted by Phase 40.1's own commit `41d2683`). A two-endpoint hunk-attribution census
  (this plan's method, and `41-RESEARCH.md`'s) can only attribute a line to a function that appears
  in one of the two endpoint snapshots' `def`-line lists; a function whose entire lifecycle (birth
  and death) falls strictly between the two endpoints leaves no trace in either snapshot's function
  list, so no diff line can ever be attributed to it by this method. This is a structural blind spot
  of two-endpoint hunk attribution, not a hidden coverage gap: the deletion's real effect — the
  caller now calling `_reference_anchor_decision` directly — is fully captured via `visit_reference`
  (row 3's coverage), and `40.1-NONREGRESSION.md` §4 itself records rows 3 and 4 as "one indivisible
  fix" sharing the same RED. Stated explicitly here rather than left silent.

---

## This phase's own translator change (D-12 classification)

`visit_desc_sig_name`'s docstring carries a real edit this phase (commit `c81ca29`, "escape the
unbalanced asterisk in `visit_desc_sig_name`'s docstring (D-12)"), which is why `visit_desc_sig_name`
appears in Task 2's census. This is classified here, on its own measurement:

```
$ git show c81ca29 -- typsphinx/translator.py
diff --git a/typsphinx/translator.py b/typsphinx/translator.py
index a63f79c..136eb97 100644
--- a/typsphinx/translator.py
+++ b/typsphinx/translator.py
@@ -6602,7 +6602,7 @@ class TypstTranslator(SphinxTranslator):
         one becomes nodes.reference. A pending_xref check here would
         silently never fire -- this is the exact wrong turn
         37-CONTEXT.md's own D-05 text invites; 37-04-SUMMARY.md's
-        unresolved-C-domain-type measurement (PyTypeObject *type, no
+        unresolved-C-domain-type measurement (``PyTypeObject *type``, no
         intersphinx) independently confirms the mechanical rule-2 output
         this discriminator produces for a type that never resolves.
         """
```

The single changed line sits inside `visit_desc_sig_name`'s docstring (the method's `def` is at
line 6564; its docstring runs to the closing `"""` this hunk's last context line shows; the first
executable statement, `parent = node.parent`, follows immediately after). **No `self.`, `return`,
`if`, `raise`, or `def` line moved** — the change wraps an already-documented C type expression in
RST inline-literal backticks so a lone `*` no longer parses as an unterminated inline-emphasis
start-string.

**Classification: DOCSTRING-ONLY.** This change:

- Alters no emitted `.typ` shape — the executable body of `visit_desc_sig_name` (rules 1/2/3 of the
  D-05 discriminator) is byte-identical before and after this commit.
- Creates NO GATE-01 fixture obligation under milestone invariant #4 — there is no behavioural
  change for a fixture to pin.
- Is proven by this plan's OWN measurement above (the commit's full diff, re-run against the
  current range), not merely cross-referenced from the commit message's own claim.

**`visit_desc_sig_name` also carries real Phase 37-era behavioural changes in this same range** —
it is one of the four handlers with match-count 4 in Task 2's coverage table
(`test_desc_sig_space_render_gate.py`, `test_desc_signature_concat_render_gate.py`,
`test_signature_typography_gate.py`, `test_translator.py`), covering its D-05 discriminator's three
rules (SIG-04's italic parameter name, the C++ non-leaf `desc_name` bold-wrapping case, and the
unresolved-type fallthrough this very docstring documents). **Both facts are on the record
together:** the handler's *behaviour* is gate-covered from Phase 37; this phase's *docstring* edit
inside the same handler carries no separate fixture obligation.

---

## SC#4 verdict

| Invariant | What was measured | By which command(s) | Verdict |
|---|---|---|---|
| 1 — zero new runtime dependencies | `pyproject.toml`'s `dependencies` array and `[dependency-groups]` table, both sides of the range; `uv.lock`'s third-party version movement | `git diff BASE..HEAD -- pyproject.toml`, `git show {BASE,HEAD}:pyproject.toml \| sed -n '/^dependencies/,/^\]/p'`, `git diff --stat/-- uv.lock`, `grep -E '^[+-]name = \|^[+-]version = '` | **PROVEN**, with a stated non-breaching finding: the `dev` extra (not `dependencies` or `[dependency-groups]`) gained one dev-only package (`pillow`, Phase 39 D-07) — outside the runtime-dependency scope the invariant and CHANGELOG claim 1 actually assert |
| 2 — the `@preview` surface | All three declaration sites, both sides of the range; every newly added file carrying a `@preview` import, classified | `grep -n "@preview" {writer.py,template_engine.py,base.typ}` on both `HEAD` and `git show BASE:...`; `git diff --diff-filter=A --name-only \| xargs grep -l "@preview"`; `uv run pytest tests/test_preview_version_sync.py -v` | **PROVEN** — three sites line-for-line identical, four package versions unchanged, no new production sync site, two genuine fixture-mirrors both current, `docs/`'s pre-existing fourth site named as a carried Warning |
| 3 — every node-handler change carries a recorded-RED GATE-01 fixture | The hunk-attributed handler census (51 handlers, re-derived); the node-name coverage map (all 51 mapped); the 3 single-hit handlers spot-checked against real assertions and a doctree-confirmed node occurrence; Phase 40.1's 4-row RED manifest folded in with existence + SHA-resolution confirmation; D-12's own change classified as docstring-only with its own proof | `census.py` (hunk attribution over `git diff -U0`), `coverage_map.py` (node-name grep over `tests/*.py`), `inspect_doctree.py` (real doctree node enumeration), `test -f` / `git cat-file -e` for the 40.1 fold-in, `git show c81ca29` for D-12 | **PROVEN**, within this plan's own defined scope: the 48 multi-hit handlers rest on the node-name coverage map's "necessary but not sufficient" strength (per-hunk assertion tracing for all 48 was not independently performed — only the 3 single-hit rows, per this plan's own acceptance criteria and `41-RESEARCH.md` Open Question 2's recommendation) |

**No invariant is NOT PROVEN.** Invariant 3's PROVEN verdict carries one explicit scope
qualification (above) rather than an unqualified blanket claim — stated so a future reader does not
read "PROVEN" as "every one of 51 handlers individually assertion-traced."

### Executed versus skipped — a skip is not a pass (every command in this file)

| Command | Executed? | Skipped anything? |
|---|---|---|
| `git merge-base main HEAD` / `git describe --tags` / `git rev-parse HEAD` / commit count | Yes — all ran, fresh values recorded | None |
| `git merge-base --is-ancestor` (×3, Phase 40.1 commits) / `git log ... \| grep 40.1` | Yes — all ran, all confirmed ancestors | None |
| `git diff BASE..HEAD -- pyproject.toml` (full diff) | Yes | None |
| `git show {BASE,HEAD}:pyproject.toml \| sed` (dependencies array, both sides) | Yes | None |
| `git diff --stat/full -- uv.lock` + `grep -E name/version` | Yes | None |
| `git log --oneline --all \| grep pillow` | Yes | None |
| `grep -n "@preview"` (HEAD, 3 files) / `git show BASE:... \| grep` (3 files) | Yes — all 6 invocations ran | None |
| `git diff --diff-filter=A --name-only \| xargs grep -l "@preview"` | Yes | None |
| `git diff --stat -- docs/` | Yes (empty result, confirmed) | None |
| `uv run pytest tests/test_preview_version_sync.py -v` | Yes — all 3 collected ran | None — 3 passed |
| `census.py` (hunk-attributed handler census) | Yes | None |
| `coverage_map.py` (node-name grep over `tests/*.py`) | Yes — all 51 handlers processed | None |
| `sphinx-build -b typstpdf` on `tests/fixtures/desc_sig_space_render_gate` | Yes — real build, real PDF produced | None |
| `inspect_doctree.py` (real doctree node enumeration) | Yes | None |
| `test -f` (×3, 40.1 evidence files) / `git cat-file -e` (×3, 40.1 RED SHAs) | Yes — all 6 ran | None — all 6 confirmed |
| `git show c81ca29 -- typsphinx/translator.py` (D-12 diff) | Yes | None |
| `git status --porcelain -- typsphinx tests scripts` (×2, after Task 1/2/3) | Yes — run repeatedly | None — empty every time |

**No command anywhere in this file returned a skip standing in for a pass.** Every invariant, every
spot-check, and every fold-in confirmation rests on a command that genuinely ran to a real observed
result in this worktree.

---

## Scratch tooling — final confirmation

Three scratch scripts were used across this file's three tasks: `census.py`, `coverage_map.py`,
`diffcheck.py`, and `inspect_doctree.py` — all under `/tmp/claude-1000/.../scratchpad/`, none
`git add`ed, none referenced by any committed file.

```
$ git status --porcelain -- typsphinx tests scripts
(no output)
```

No census/coverage/spot-check tooling was added anywhere in this repository.


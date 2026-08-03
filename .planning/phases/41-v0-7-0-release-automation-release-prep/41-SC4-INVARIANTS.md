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

<!-- gsd:write-continue -->

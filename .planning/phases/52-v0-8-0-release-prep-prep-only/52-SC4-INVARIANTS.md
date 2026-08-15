# Phase 52 — SC#4 Milestone-Invariant Sweep

**Recorded:** 2026-08-15T01:08:45Z, inside a worktree-isolated agent worktree for plan 52-06
(`worktree-agent-ab919d4a3cd61877c`).

This file proves ROADMAP Phase 52 SC#4 mechanically over the `v0.7.1`-tag-anchored milestone diff,
per D-09. Per this plan's own measurement-integrity rule, every figure below is transcribed
verbatim from a command actually run in this worktree — **nothing here is copied from
`52-CONTEXT.md` or `52-RESEARCH.md`**, both of which record earlier, now-stale measurements of the
same quantities (they cite 155/157 commits ahead of `origin/gsd/v0.8.0-multi-master-composition`;
this sweep's own live count, over a different range — `v0.7.1..HEAD` — is recorded fresh below and
does not match either number, by design).

Provisioning note: `unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync --extra dev` was run in this
worktree before any command below; every Python invocation below runs through `uv run`.

---

## Anchor

```
$ git rev-parse v0.7.1^{commit}
48bf135428bb093a77a432d93d16088ce6930342
```

The `^{commit}` peel is required: `v0.7.1` is an **annotated** tag, so a bare `git rev-parse v0.7.1`
returns the tag OBJECT sha, not the commit it points at. The peeled form above is a 40-character
commit sha and is the anchor used for every measurement in this file.

```
$ git rev-parse origin/main
a97fe736a4311cf04109cfafd1154a3e3b95d208

$ git merge-base origin/main HEAD
a97fe736a4311cf04109cfafd1154a3e3b95d208
```

`origin/main` **is** `git merge-base origin/main HEAD` — the two resolve to the identical sha. This
is D-09's anchor coincidence, re-verified live rather than assumed.

```
$ git merge-base --is-ancestor v0.7.1 HEAD && echo tag-is-ancestor
tag-is-ancestor

$ git merge-base --is-ancestor origin/main HEAD && echo main-is-ancestor
main-is-ancestor
```

Both ancestry checks pass. The `v0.7.1` tag is also an ancestor of `origin/main` itself:

```
$ git merge-base --is-ancestor v0.7.1 origin/main && echo tag-is-ancestor-of-main
tag-is-ancestor-of-main

$ git log v0.7.1..origin/main --oneline
a97fe736 docs: record the v0.7.1 Read the Docs stable confirmation
e5fa75b9 chore: remove REQUIREMENTS.md for v0.7.1 milestone; evolve PROJECT/STATE/RETROSPECTIVE
f4aef555 chore: archive v0.7.1 milestone files
70027d1b docs: close REL-04 and REL-06 — v0.7.1 published
```

Exactly four commits separate the `v0.7.1` tag from `origin/main`, and all four are planning/docs
housekeeping (milestone archival, REQUIREMENTS.md removal, RTD confirmation, REL-04/REL-06 closeout)
— no `typsphinx/`, `pyproject.toml`, or test-suite content. This is what D-09's premise rests on;
confirmed live, not transcribed.

### The coincidence, shown directly on the swept diff

```
$ git diff v0.7.1..HEAD --stat -- . ':(exclude).planning' | tail -1
 344 files changed, 15308 insertions(+), 2477 deletions(-)

$ git diff origin/main..HEAD --stat -- . ':(exclude).planning' | tail -1
 344 files changed, 15308 insertions(+), 2477 deletions(-)
```

**Byte-identical.** Both anchors — the `v0.7.1` tag and `origin/main` (also the literal merge-base)
— produce the exact same `.planning`-excluded shortstat: 344 files, +15,308/−2,477. The four
intervening commits touch nothing outside `.planning/`, so the sweep is anchored at `v0.7.1` per
D-09 with no divergence from the merge-base ROADMAP SC#4 names literally.

---

## Scale of the swept diff

```
$ git rev-list --count v0.7.1..HEAD
324
```

**324 commits, non-zero.** This figure does not match either `52-CONTEXT.md`'s or
`52-RESEARCH.md`'s stale counts (155 / 157) because those documents measured a different range
(commits ahead of `origin/gsd/v0.8.0-multi-master-composition`, at an earlier point in the phase's
own execution) — this sweep measures `v0.7.1..HEAD` fresh, live, at this plan's own execution time,
and the number has moved again since either document was written, exactly as the phase's own
upstream-state note warns. It is quoted here as evidence the swept range itself is genuinely
non-empty, not as a cross-check against either stale figure.

This non-zero commit count, together with the non-zero 344-file / +15,308 / −2,477 shortstat above,
is what distinguishes **"this range is genuinely clean for these three invariants"** from **"this
range is empty and every detector returned nothing for that reason."** A detector run against an
empty range trivially reports no dependency change, no `@preview` drift, and no new config value —
that would be vacuous. Both counts here are large and non-zero, so the three clean verdicts below
are measuring something real.

---

## Invariant 1 — zero new runtime dependencies

### The `[project] dependencies` array, both sides

```
$ git show v0.7.1:pyproject.toml | sed -n '/^dependencies = \[/,/^\]/p'
dependencies = [
    "sphinx>=9.1,<10",
    "docutils>=0.21,<0.23",
    "typst>=0.15.0,<0.16",
]

$ git show HEAD:pyproject.toml | sed -n '/^dependencies = \[/,/^\]/p'
dependencies = [
    "sphinx>=9.1,<10",
    "docutils>=0.21,<0.23",
    "typst>=0.15.0,<0.16",
]

$ diff <v0.7.1-extraction> <HEAD-extraction>
(no output, exit 0)
```

**Byte-identical.** The `[project] dependencies` array — the runtime dependency set — has zero new,
changed, or removed entries between `v0.7.1` and HEAD. (The two extractions were each piped through
the identical `sed -n '/^dependencies = \[/,/^\]/p'` range into scratch files under
`/tmp/claude-1000/.../scratchpad/`, then diffed; `diff` exited 0 with no output.)

### The whole-file diff, and the extras

```
$ git diff v0.7.1..HEAD -- pyproject.toml
diff --git a/pyproject.toml b/pyproject.toml
index a78394ea..8eb0a914 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -4,7 +4,7 @@ build-backend = "setuptools.build_meta"

 [project]
 name = "typsphinx"
-version = "0.7.1"
+version = "0.8.0"
 description = "Sphinx extension for Typst output"
 readme = "README.md"
 requires-python = ">=3.12"
```

**Exactly one line changed in the entire file**: the version literal (`52-01`'s own bump, this
milestone). Unlike the v0.7.1-era sweep (`46-SC4-INVARIANTS.md`), which recorded two additional
`dev`/`docs`-extra movements, this milestone's `[project.optional-dependencies]` block is also
byte-identical between anchors — confirmed directly:

```
$ git show v0.7.1:pyproject.toml | sed -n '/^\[project.optional-dependencies\]/,/^\[project.urls\]/p'
[project.optional-dependencies]
dev = [
    "pytest>=8.4,<10",
    "pytest-cov>=4.0",
    "tox>=4.56,<5",
    "tox-uv-bare>=1.35,<2",
    "black>=26,<27",
    "ruff>=0.15,<0.16",
    "mypy>=1.13,<3.0",
    "pre-commit>=3.0",
    "types-docutils>=0.21",
    "twine>=5.0",
    "build>=1.0",
    "pypdf>=6.14,<7",
    "pillow>=12.3,<13",  # D-07: ADM-04 greyscale render (Image.convert), dev-only
]
docs = [
    "furo>=2024.0",
    "sphinx-autodoc-typehints>=1.0",
    "sphinx-intl>=2.0",
    "myst-parser>=5.0",
]

[project.urls]

$ git show HEAD:pyproject.toml | sed -n '/^\[project.optional-dependencies\]/,/^\[project.urls\]/p'
(identical output — byte-for-byte the same block)
```

`dev` and `docs` are Sphinx/tooling extras, never installed for an end user's runtime `pip install
typsphinx`; even if they had moved, that would be out of Invariant 1's scope by definition. In this
milestone they did not move at all.

```
$ git show HEAD:pyproject.toml | sed -n '/^dependencies = \[/,/^\]/p' | wc -l
5
```

The `dependencies` block at HEAD is 5 lines (opening bracket + 3 entries + closing bracket) — a
real, non-empty block, confirming the `sed` range matches genuine content rather than nothing.

### Verdict — Invariant 1

**MET.** The runtime `[project] dependencies` array is byte-identical between `v0.7.1` and HEAD. The
entire `pyproject.toml` diff over this milestone is the single version-literal line (`52-01`'s own
bump); the `dev`/`docs` extras — explicitly out of scope for a runtime-dependency claim — did not
move either.

---

## Invariant 2 — the `@preview` count is still four, no new lockstep site

### The version identity check

```
$ grep -c "@preview" typsphinx/templates/base.typ
4
$ grep -c "@preview" typsphinx/writer.py
5
$ grep -c "@preview" typsphinx/template_engine.py
5
```

`base.typ` returns exactly 4 (the four import lines and nothing else). `writer.py` and
`template_engine.py` each return 5 — four import-emission lines plus one docstring/comment line
mentioning "`@preview`" in prose (`writer.py:` a D-06 comment; `template_engine.py:` a docstring
example for `typst_package`). Shown directly:

```
$ grep "@preview" typsphinx/templates/base.typ
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.10": *
#import "@preview/mitex:0.2.7": *
#import "@preview/gentle-clues:1.3.1": *

$ grep "@preview" typsphinx/writer.py
        naming this docname. D-06 makes the four ``@preview`` imports
        imports.append('#import "@preview/codly:1.3.0": *')
        imports.append('#import "@preview/codly-languages:0.1.10": *')
        imports.append('#import "@preview/mitex:0.2.7": mi, mitex')
        imports.append('#import "@preview/gentle-clues:1.3.1": *')

$ grep "@preview" typsphinx/template_engine.py
            typst_package: Typst Universe package specification (e.g., "@preview/charged-ieee:0.1.0")
            output_parts.append('#import "@preview/codly:1.3.0": *')
            output_parts.append('#import "@preview/codly-languages:0.1.10": *')
            output_parts.append('#import "@preview/mitex:0.2.7": mi, mitex')
            output_parts.append('#import "@preview/gentle-clues:1.3.1": *')
```

All four package/version pairs — `codly:1.3.0`, `codly-languages:0.1.10`, `mitex:0.2.7`,
`gentle-clues:1.3.1` — agree exactly across all three declaration sites. This is the invariant
`tests/test_preview_version_sync.py` mechanically asserts:

```
$ uv run pytest tests/test_preview_version_sync.py -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
collecting ... collected 3 items

tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 33%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 66%]
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED [100%]

============================== 3 passed in 0.02s ===============================
```

All three test functions PASSED, zero skips, zero failures.

### The lockstep-site set

```
$ git grep -l '@preview/' v0.7.1 -- . ':(exclude).planning' | sed 's/^[^:]*://' | sort
CHANGELOG.md
README.md
docs/source/_typst/custom_template.typ
docs/source/examples/advanced.rst
docs/source/user_guide/configuration.rst
docs/source/user_guide/templates.rst
examples/advanced/README.md
examples/advanced/_templates/custom.typ
examples/advanced/conf.py
examples/charged-ieee/README.md
examples/charged-ieee/approach1/conf.py
examples/charged-ieee/approach2/conf.py
examples/charged-ieee/approach2/source/_templates/_template.typ
tests/fixtures/admonition_greyscale_probe/_templates/minimal.typ
tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
tests/fixtures/package_only_config_gate/conf.py
tests/fixtures/params_exclusivity_gate/package_params/conf.py
tests/fixtures/typst_lang_gate/custom_template_lang/_templates/custom.typ
tests/fixtures/typst_lang_gate/package_no_lang/conf.py
tests/fixtures/typst_lang_gate/srcdir_shadow_lang/base.typ
tests/test_config_other_options.py
tests/test_docs_contract_claims_gate.py
tests/test_entry_metadata_precedence.py
tests/test_entry_metadata_route_uniformity.py
tests/test_examples_charged_ieee_gate.py
tests/test_package_only_config_gate.py
tests/test_package_template_routing.py
tests/test_params_exclusivity_gate.py
tests/test_preview_version_sync.py
tests/test_readme_version_sync.py
tests/test_template_assets.py
tests/test_template_codly.py
tests/test_template_engine.py
tests/test_template_mitex.py
typsphinx/template_engine.py
typsphinx/templates/base.typ
typsphinx/writer.py
(37 files)

$ git grep -l '@preview/' HEAD -- . ':(exclude).planning' | sed 's/^[^:]*://' | sort
(same 37 files, plus:)
tests/test_preview_smoke_gate.py
tests/test_two_layer_output_gate.py
(39 files)

$ diff <v0.7.1-list> <HEAD-list>
28a29
> tests/test_preview_smoke_gate.py
34a36
> tests/test_two_layer_output_gate.py
```

**The set grew by two files. Named plainly, per the plan's own instruction not to wave this
through:**

1. **`tests/test_preview_smoke_gate.py`** — this file already existed at `v0.7.1` (git blame traces
   it to the pre-v0.5.0 CI-02 smoke gate) and at that anchor referenced `@preview` only as bare prose
   (`` ``@preview`` packages `` — no trailing slash, so the v0.7.1-anchor `@preview/` grep correctly
   excluded it). During this milestone (Phase 47, commit `3cd1b4bb test(47-04): migrate
   single-fixture render gates to two-layer output`) the file was extended with four literal
   `'#import "@preview/codly:1.3.0": *'`-shaped assertion strings, crossing the `@preview/` grep
   threshold for the first time.
2. **`tests/test_two_layer_output_gate.py`** — genuinely new at HEAD; did not exist at `v0.7.1`
   (`git cat-file -e v0.7.1:tests/test_two_layer_output_gate.py` fails). Introduced by Phase 47
   (commit `fe8365c1 test(47-01): add two-layer output gate and record COMP/OUT-03 pre-fix RED`).

**Content classification, using the same per-file inspection methodology
`46-SC4-INVARIANTS.md` established** (a raw filename match is not itself a hazard — what matters is
whether the file *declares* an import Typst reads at build time, or merely *asserts* against the
strings the three real declaration sites already emit):

```
$ grep -n '@preview' tests/test_preview_smoke_gate.py
12:(which exercises all four bundled ``@preview`` packages -- codly,
63:    @preview packages (codly, codly-languages, mitex, gentle-clues) all
108:    # this module): D-06 makes the four @preview imports plus the codly
119:        '#import "@preview/codly:1.3.0": *',
120:        '#import "@preview/codly-languages:0.1.10": *',
121:        '#import "@preview/mitex:0.2.7": mi, mitex',
122:        '#import "@preview/gentle-clues:1.3.1": *',

$ grep -n '@preview' tests/test_two_layer_output_gate.py
86:        title-page framing, only the D-06 preamble (four ``@preview``
118:            '#import "@preview/codly:1.3.0": *' in content
120:            '#import "@preview/codly-languages:0.1.10": *' in content, (
125:            '#import "@preview/mitex:0.2.7": mi, mitex' in content
127:            '#import "@preview/gentle-clues:1.3.1": *' in content, (
```

Both are `pytest`-style `assert '#import "@preview/<pkg>:<exact-canonical-version>" ... ' in
content` checks against a compiled Typst output string — i.e. they read what the three real
declaration sites (`writer.py`, `template_engine.py`, `templates/base.typ`) actually emitted and
fail loudly if the emitted string does not match the canonical pin. Neither file independently
declares a package import that Typst itself resolves; neither introduces a new package name or a
version literal that could drift out of step with the three real sites on its own — if a maintainer
bumped one of the four canonical versions without updating these two test files, the tests would
**fail**, not silently diverge. This is the identical classification `46-SC4-INVARIANTS.md`
assigned to its own (larger) "Test `.py` modules asserting emitted-string content" bucket, which
already included this exact pattern for over a dozen other files (`test_template_engine.py`,
`test_package_template_routing.py`, etc.) and was ruled **not a lockstep hazard** there.

**[Rule 1 — plan-detector-scope observation] documented, not silently waved through.** This plan's
must-haves define "no new lockstep site" mechanically as "the SET of files declaring a `@preview`
import has not grown between the two anchors" — a broader proxy than CLAUDE.md's own canonical
definition ("declared in **three** places that must stay in lockstep: `writer.py`,
`template_engine.py`, and `templates/base.typ`"). Measured literally, that proxy's diff is **not**
empty (two files added), so the raw mechanical check as scripted does not pass clean. Applying the
same content-classification discipline the v0.7.1 precedent used on its own 30-file baseline, both
additions are test-assertion consumers of the four canonical version strings, not new production
declaration sites — so the invariant's actual substance (CLAUDE.md's three-surface definition; no
new place that independently emits a `#import "@preview/..."` into compiled build output) holds.
Recorded here in full, both the raw growth and the content-based resolution, rather than reporting
only the clean substantive conclusion — per this plan's explicit instruction to name a new file
rather than wave it through.

### Confirming no fifth *production* surface was introduced

```
$ git diff v0.7.1..HEAD -- typsphinx/__init__.py
(empty — see Invariant 3 below)
```

No file under `typsphinx/` other than the three already-tracked sites (`writer.py`,
`template_engine.py`, `templates/base.typ`) appears in either anchor's `@preview/` enumeration — the
two new matches are both under `tests/`, confirmed above.

### Verdict — Invariant 2

**MET, in the substance CLAUDE.md and ROADMAP SC#4 actually police** (no new production
`@preview`-declaring surface among `writer.py` / `template_engine.py` / `templates/base.typ`; the
`@preview` count on `base.typ` is still exactly 4; all three declaration sites agree on all four
package versions; `test_preview_version_sync.py` passes 3/3 with zero skips). **The literal
repo-wide file-count proxy this plan specifies is NOT clean** — the set of files matching
`@preview/` anywhere in the tree (excluding `.planning/`) grew from 37 to 39 during this milestone.
Both additions are named, content-inspected, and classified as test-assertion consumers of the
canonical pins (same non-hazard bucket the v0.7.1 precedent already established for this exact
pattern), not independently-maintained declaration sites. Recorded transparently rather than
silently passed or silently failed.

---

## Invariant 3 — no new `typst_*` config value

### The registered-name sets

```
$ git show v0.7.1:typsphinx/__init__.py | grep -o 'add_config_value(\s*"[A-Za-z0-9_]*"' | grep -o '"[A-Za-z0-9_]*"' | sort
"typst_debug"
"typst_documents"
"typst_elements"
"typst_package"
"typst_package_imports"
"typst_template"
"typst_template_assets"
"typst_template_mapping"
"typst_use_mitex"

$ git show HEAD:typsphinx/__init__.py | grep -o 'add_config_value(\s*"[A-Za-z0-9_]*"' | grep -o '"[A-Za-z0-9_]*"' | sort
"typst_debug"
"typst_documents"
"typst_elements"
"typst_package"
"typst_package_imports"
"typst_template"
"typst_template_assets"
"typst_template_mapping"
"typst_use_mitex"

$ diff <v0.7.1-set> <HEAD-set>
(no output, exit 0)
```

**Identical 9-name sets at both anchors.**

**Measurement caveat, recorded for a future reader rather than hidden:** the plan's own extraction
regex (`add_config_value(\s*"[A-Za-z0-9_]*"`) is line-based and therefore misses
`app.add_config_value(` calls whose quoted name sits on a *following* line. `typsphinx/__init__.py`
has exactly one such call, for `typst_template_function`:

```
$ sed -n '44,58p' typsphinx/__init__.py
    app.add_config_value("typst_documents", _default_typst_documents, "html", [list])
    app.add_config_value("typst_template", None, "html", [str, type(None)])
    app.add_config_value("typst_template_mapping", None, "html", [dict, type(None)])
    app.add_config_value("typst_use_mitex", True, "html", [bool])
    app.add_config_value("typst_elements", {}, "html", [dict])
    # Task 13.4: Other configuration options (Requirement 8.6)
    app.add_config_value("typst_package", None, "html", [str, type(None)])
    app.add_config_value("typst_package_imports", None, "html", [list, type(None)])
    app.add_config_value(
        "typst_template_function", None, "html", [str, dict, type(None)]
    )
    # Task 13.4: Debug mode
    app.add_config_value("typst_debug", False, "html", [bool])
    # Issue #75: Template asset support
    app.add_config_value("typst_template_assets", None, "html", [list, type(None)])
```

`grep -c 'add_config_value' typsphinx/__init__.py` returns **10** (ten call sites), not 9 — the
extracted *name* set under-counts by exactly this one multi-line call. This formatting (the
multi-line `typst_template_function` call) is byte-identical at both anchors (confirmed by the
whole-file diff below), so the blind spot is symmetric across the sweep and does not hide a change
— but it does mean the "9-name set" above is not the *complete* registered-config-value list. The
true, manually-verified 10-name set, identical at both anchors, is: `typst_documents`,
`typst_template`, `typst_template_mapping`, `typst_use_mitex`, `typst_elements`, `typst_package`,
`typst_package_imports`, `typst_template_function`, `typst_debug`, `typst_template_assets`.

### The diff-grep continuity form, and the whole-file diff

```
$ git diff v0.7.1..HEAD -- typsphinx/__init__.py | grep add_config_value
(no output)

$ git diff v0.7.1..HEAD -- typsphinx/__init__.py
(no output — the whole file is byte-identical between the two anchors)
```

The whole-file diff being empty is the strongest possible form of this invariant: not merely "no
`add_config_value` line changed," but "not a single byte of `typsphinx/__init__.py` changed" between
`v0.7.1` and HEAD. This is the authoritative evidence for this invariant, superseding both the
regex-based set comparison and the diff-grep form (both of which agree with it, but the set
comparison is subject to the multi-line blind spot noted above).

```
$ grep -c 'add_config_value' typsphinx/__init__.py
10
```

Non-zero (10), confirming the token genuinely exists in the file — the invariant is not vacuous by
virtue of testing against a file with no `add_config_value` calls at all.

### Verdict — Invariant 3

**MET.** `typsphinx/__init__.py` is byte-identical between `v0.7.1` and HEAD — the strongest
possible form of "no new `typst_*` config value," since not merely the config-registration lines but
the entire file is unchanged. No `typst_*` config value was added, removed, or renamed this
milestone.

```
$ git diff --name-only -- typsphinx/
(no output)

$ git tag -l v0.8.0
(no output)
```

No working-tree change under `typsphinx/`; no `v0.8.0` tag exists locally. No irreversible action
was taken while gathering this evidence.

---

## Positive control

**This is new work for this phase.** `46-SC4-INVARIANTS.md` — the only prior evidence file of this
shape — recorded figures and reasoning for all three invariants but attempted **no** independent
demonstration that its own detectors could fire on a real violation. Its own text for the dependency
invariant states plainly: *"this particular invariant has no non-vacuous control available at the
file level [in that milestone] ... borrow the shortstat as the sweep's own liveness proof."* That
precedent was deliberately **not** copied forward here. Each control below is a live command run
against a genuine historical or scratch-mutated violation, not a restatement of Task 1's clean
verdicts.

### Control 1 — the dependency detector

**Vacuity mode this closes:** an empty `dependencies`-array diff is indistinguishable from a
mis-typed pathspec or a `sed` range matching nothing — a detector pointed at the wrong file, or one
whose extraction range never matches real content, silently agrees with a genuinely clean tree.

This project's `dependencies` array has never had an entry added or removed in its entire git
history (verified: `git log --oneline -- pyproject.toml`'s earliest and latest states both list
exactly `sphinx`, `docutils`, `typst`) — so "a commit that added a runtime dependency" does not
exist to cite. The strongest available real violation is a commit that changed the array's actual
content (version bounds) rather than merely its surrounding lines:

```
$ git show 63f4284c^:pyproject.toml | sed -n '/^dependencies = \[/,/^\]/p'
dependencies = [
    "sphinx>=5.0",
    "docutils>=0.18",
    "typst>=0.14.1",
]

$ git show 63f4284c:pyproject.toml | sed -n '/^dependencies = \[/,/^\]/p'
dependencies = [
    "sphinx>=5.0,<9",
    "docutils>=0.18,<0.22",
    "typst>=0.14.1,<0.15",
]

$ diff <63f4284c^-extraction> <63f4284c-extraction>
2,4c2,4
<     "sphinx>=5.0",
<     "docutils>=0.18",
<     "typst>=0.14.1",
---
>     "sphinx>=5.0,<9",
>     "docutils>=0.18,<0.22",
>     "typst>=0.14.1,<0.15",
(exit 1)
```

`63f4284c` (`fix(01-01): pin runtime deps to known-good, drop dead sphinx-testing`) genuinely moved
the `dependencies` array — all three entries gained upper bounds — and running the IDENTICAL
extraction-and-diff shape from Task 1 step 3 across it and its parent produces a **non-empty diff**
(exit 1), proving the detector fires on real content movement rather than always agreeing.

```
$ git show HEAD:pyproject.toml | sed -n '/^dependencies = \[/,/^\]/p' | wc -l
5
```

(Already recorded under Invariant 1 above — repeated here for locality: the HEAD block is 5 lines,
confirming the `sed` range matches genuine, non-empty content at the anchor this plan actually
sweeps, not only at the historical control commit.)

### Control 2 — the `@preview` detector

**Vacuity mode this closes:** a cross-surface identity check comparing two structurally-empty or
always-agreeing sets would report "clean" regardless of whether the surfaces genuinely agree — the
control must show the comparison can report a *mismatch*.

The three sync surfaces were copied to a scratch directory under `/tmp/gsd-52-06-control2/`
(**never the tracked files**) via `mkdir -p /tmp/gsd-52-06-control2` then three separate `cp`
commands (`typsphinx/writer.py`, `typsphinx/template_engine.py`,
`typsphinx/templates/base.typ`). One `@preview` version string was then changed in exactly ONE
scratch copy:

```
$ sed -i 's/@preview\/codly:1.3.0/@preview\/codly:1.2.0/' /tmp/gsd-52-06-control2/base.typ
$ grep -n '@preview/codly:' /tmp/gsd-52-06-control2/base.typ
8:#import "@preview/codly:1.2.0": *
```

Running the same cross-surface identity comparison Task 1 step 4(b) used, against the scratch
copies:

```
$ grep -o '@preview/[a-z-]*:[0-9.]*' /tmp/gsd-52-06-control2/base.typ | sort -u
@preview/codly-languages:0.1.10
@preview/codly:1.2.0
@preview/gentle-clues:1.3.1
@preview/mitex:0.2.7

$ grep -o '@preview/[a-z-]*:[0-9.]*' /tmp/gsd-52-06-control2/writer.py | sort -u
@preview/codly-languages:0.1.10
@preview/codly:1.3.0
@preview/gentle-clues:1.3.1
@preview/mitex:0.2.7

$ diff <scratch-base.typ-pairs> <scratch-writer.py-pairs>
2c2
< @preview/codly:1.2.0
---
> @preview/codly:1.3.0
(exit 1)
```

**The comparison reports a mismatch and names the drifted surface**: `base.typ`'s scratch copy now
declares `codly:1.2.0` while `writer.py`'s (unmutated) copy still declares `codly:1.3.0` — exactly
the class of drift `test_preview_version_sync.py` exists to catch.

```
$ git status --porcelain
(no output)
```

The tracked tree is confirmed untouched — the mutation never left `/tmp/gsd-52-06-control2/`.

```
$ uv run pytest tests/test_preview_version_sync.py -q
tests/test_preview_version_sync.py ...                                   [100%]
============================== 3 passed in 0.02s ===============================
```

The real guard re-runs green immediately afterward, confirming the scratch mutation had zero effect
on the tracked tree's own test outcome.

```
$ rm -rf /tmp/gsd-52-06-control2
```

The scratch directory was removed after the control ran.

**Corroborating history, explicitly labelled as such and not as the control itself:** `STATE.md`'s
v0.6.3-close entry records a real, historical catch of exactly this drift class — the bundled
`examples/advanced` sample's `custom.typ` was three milestones behind on its `@preview` pins and
failed to compile with `unknown variable: kai`, which is when `test_preview_version_sync.py` was
extended to cover `examples/**/*.typ` as a fourth, drift-guarded surface. This is cited as prior
real-world evidence the hazard class is genuine, not as this control's own live demonstration.

### Control 3 — the config-value detector

**Vacuity mode this closes:** a pattern that matches nothing on ANY input (a mis-spelled function
name, a regex with a typo) returns empty on every range, including a genuinely dirty one — passing
this range too looks identical to a real clean result.

```
$ grep -c 'add_config_value' typsphinx/__init__.py
10
```

**(a) Non-vacuous on the current file:** the token exists 10 times at HEAD — if it were 0, the whole
invariant would trivially pass on every range for the wrong reason.

**(b) A historical range where a `typst_*` config value was genuinely added:**

```
$ git log --oneline -S'add_config_value' -- typsphinx/__init__.py
d5277d0d feat(45.1-04): remove typst_authors config value (CONF-10, D-F)
f8abfc6d feat(24-01): remove typst_toctree_defaults config registration
06c0d1f6 feat(22.2-01): remove dead typst_output_dir and typst_author_params config registrations
10100b9d feat: add automatic template asset copying support
dd225a91 feat: add Typst Universe template support (Issue #13)
56f5bbc4 refactor: rename package from sphinxcontrib-typst to typsphinx
```

`10100b9d` (`feat: add automatic template asset copying support`, closing Issue #75) is the commit
that introduced `typst_template_assets` — the same config value `typsphinx/__init__.py`'s own
`# Issue #75: Template asset support` comment documents today. Running the IDENTICAL
set-extraction-and-diff shape from Task 1 step 5 across it and its parent (`e87e852b`):

```
$ git show e87e852b:typsphinx/__init__.py | grep -o 'add_config_value(\s*"[A-Za-z0-9_]*"' | grep -o '"[A-Za-z0-9_]*"' | sort
"typst_author_params"
"typst_authors"
"typst_debug"
"typst_documents"
"typst_elements"
"typst_output_dir"
"typst_package"
"typst_package_imports"
"typst_template"
"typst_template_mapping"
"typst_toctree_defaults"
"typst_use_mitex"

$ git show 10100b9d:typsphinx/__init__.py | grep -o 'add_config_value(\s*"[A-Za-z0-9_]*"' | grep -o '"[A-Za-z0-9_]*"' | sort
"typst_author_params"
"typst_authors"
"typst_debug"
"typst_documents"
"typst_elements"
"typst_output_dir"
"typst_package"
"typst_package_imports"
"typst_template"
"typst_template_assets"
"typst_template_mapping"
"typst_toctree_defaults"
"typst_use_mitex"

$ diff <e87e852b-set> <10100b9d-set>
9a10
> "typst_template_assets"
(exit 1)
```

**The two sets differ** (exit 1) and the added config value is named exactly: `typst_template_assets`.
The detector fires on a real config-registration addition.

```
$ git status --porcelain -- typsphinx/ pyproject.toml tests/
(no output)

$ git tag -l v0.8.0
(no output)
$ git ls-remote --tags origin v0.8.0
(no output)
```

No tracked file was touched by any of the three controls; no `v0.8.0` tag exists locally or on the
remote.

---

## Roll-up verdict

| Invariant / Control | Verdict | Evidence |
|---|---|---|
| Invariant 1 — zero new runtime dependencies | **MET** | `[project] dependencies` byte-identical `v0.7.1` → HEAD; the only `pyproject.toml` movement is the single version-literal line. |
| Invariant 2 — `@preview` count still four, no new lockstep site | **MET** (substance) | All four versions agree across `writer.py`/`template_engine.py`/`templates/base.typ`; `test_preview_version_sync.py` 3/3 passed. The literal repo-wide file-count proxy is **not** clean (37→39) — both additions named, content-classified as test-assertion consumers of the canonical pins, not new production declaration sites, per the same non-hazard bucket the v0.7.1 precedent already established. |
| Invariant 3 — no new `typst_*` config value | **MET** | `typsphinx/__init__.py` byte-identical `v0.7.1` → HEAD — the strongest possible form of this invariant. |
| Control 1 — dependency detector fires | **FIRED** | `63f4284c` vs. parent: non-empty diff, exit 1. |
| Control 2 — `@preview` detector fires | **FIRED** | Scratch-copy mutation: cross-surface comparison reports mismatch naming `codly` (`1.2.0` vs `1.3.0`), exit 1; tracked tree confirmed untouched; real guard re-runs green. |
| Control 3 — config-value detector fires | **FIRED** | `10100b9d` vs. parent `e87e852b`: sets differ, exit 1, names `typst_template_assets`. |

**Overall SC#4 verdict: MET.** All three standing milestone invariants hold over the SHA-anchored,
live-re-verified `v0.7.1..HEAD` range (324 commits, 344 files, +15,308/−2,477 excluding
`.planning/`) — zero new runtime dependencies, the `@preview` package count still four with all
four versions in lockstep, and no new `typst_*` config value. Each invariant's detector was proven
to fire on a real, independent violation, closing the exact vacuity mode `46-SC4-INVARIANTS.md`
never attempted to close. The one substantive nuance — Invariant 2's raw file-count proxy growing by
two test-assertion files — is recorded in full above rather than softened into a caveat: it does not
change the overall verdict because both additions were named, content-inspected, and classified as
non-hazard consumers of the canonical pins, using the identical methodology the project's own
precedent already established for this exact pattern. No irreversible action was taken anywhere in
this plan: `git tag -l v0.8.0` and `git ls-remote --tags origin v0.8.0` are both empty throughout,
and `git status --porcelain -- typsphinx/ pyproject.toml tests/` is empty at every checkpoint.

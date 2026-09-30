# Phase 46, Plan 05 — SC#4 Milestone-Invariant Sweep (D-21 anchor)

**Recorded:** 2026-08-11T04:29:21Z, inside a worktree-agent worktree for this plan
(`worktree-agent-aa78f6244a8f98fe4`).

This file proves ROADMAP Phase 46 SC#4 mechanically over the `v0.7.0`-tag-anchored, post-merge
milestone diff, per D-21 (which supersedes D-14's `87f242a` branch-fork-point anchor). Per this
plan's own rule (measurement integrity), every figure below is transcribed verbatim from a command
actually run in this worktree — nothing here is copied from `46-CONTEXT.md` or `46-RESEARCH.md`,
both of which record earlier (now pre-merge, now-stale) measurements of the same quantities.

Provisioning note: `env -u VIRTUAL_ENV -u UV_PROJECT_ENVIRONMENT uv sync --extra dev` was run in this
worktree before any command below; every Python invocation below runs through `uv run`.

---

## Anchor

```
$ git rev-parse v0.7.0^{commit}
75fd8ed55f4fca206474f9e3aa934921588b52d5

$ git ls-remote origin refs/tags/v0.7.0
7327d0160571519d8b7c8c4ef56a19ca55756e31	refs/tags/v0.7.0
```

The `v0.7.0` tag resolves to commit `75fd8ed`, matching D-21's recorded anchor exactly. `ls-remote`
confirms the remote's annotated-tag object is `7327d01`, pointing at the same commit — same
relationship D-21 recorded.

**`87f242a` is explicitly rejected as the anchor.** D-14 originally anchored this sweep there, but
`87f242a` is one commit *after* the `v0.7.0` tag — it is merely where this milestone branch happened
to fork, not the release itself. Anchoring there would measure "this branch's own contribution since
its fork point," which is a different (and smaller/differently-scoped) quantity than "what a v0.7.0
user receives when they upgrade to v0.7.1" — the quantity the CHANGELOG's `### Verified` claims and
this sweep are actually about. D-21 supersedes D-14 for exactly this reason, and every measurement
below uses the `v0.7.0` tag (`75fd8ed`), never `87f242a`.

**Precondition confirmed:** HEAD contains `origin/main` (plan 46-01's D-20 merge landed it):

```
$ git merge-base --is-ancestor origin/main HEAD && echo "HEAD contains origin/main"
HEAD contains origin/main
```

So this sweep measures the **post-merge** tree, as D-21 requires.

---

## Scale of the swept diff

```
$ git diff v0.7.0..HEAD --stat -- . ':(exclude).planning' | tail -1
131 files changed, 11201 insertions(+), 932 deletions(-)
```

**Measured now: 131 files, +11,201 / −932.** This is larger than the pre-merge figure D-21 recorded
(126 files / +10,582 / −932) — expected, since D-21 explicitly says "these are expected to move now
that the merge and the bump have landed, so record what you measure, not what was measured before."
The merge of `origin/main` (PR #131, D-20) and the version-bump/CHANGELOG work (plans 46-02/46-03)
account for the growth. Recorded as measured, not reconciled against the stale pre-merge number.

---

## Invariant 1 — zero new runtime dependencies

### The `[project] dependencies` array, both sides

```
$ git show v0.7.0:pyproject.toml | sed -n '/^dependencies = \[/,/^\]/p'
dependencies = [
    "sphinx>=9.1,<10",
    "docutils>=0.21,<0.23",
    "typst>=0.15.0,<0.16",
]

$ sed -n '/^dependencies = \[/,/^\]/p' pyproject.toml
dependencies = [
    "sphinx>=9.1,<10",
    "docutils>=0.21,<0.23",
    "typst>=0.15.0,<0.16",
]

$ diff <extracted-v0.7.0-block> <extracted-HEAD-block>
(no output, exit 0)
```

**Byte-identical.** The `[project] dependencies` array — the runtime dependency set — has zero new,
changed, or removed entries between `v0.7.0` and HEAD.

### Broader eyeball check — the full `pyproject.toml` diff

```
$ git diff v0.7.0..HEAD -- pyproject.toml
diff --git a/pyproject.toml b/pyproject.toml
index d50c6b0..a78394e 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -4,7 +4,7 @@ build-backend = "setuptools.build_meta"

 [project]
 name = "typsphinx"
-version = "0.7.0"
+version = "0.7.1"
 description = "Sphinx extension for Typst output"
 readme = "README.md"
 requires-python = ">=3.12"
@@ -35,7 +35,7 @@ dev = [
     "pytest>=8.4,<10",
     "pytest-cov>=4.0",
     "tox>=4.56,<5",
-    "tox-uv>=1.35,<2",
+    "tox-uv-bare>=1.35,<2",
     "black>=26,<27",
     "ruff>=0.15,<0.16",
     "mypy>=1.13,<3.0",
@@ -50,6 +50,7 @@ docs = [
     "furo>=2024.0",
     "sphinx-autodoc-typehints>=1.0",
     "sphinx-intl>=2.0",
+    "myst-parser>=5.0",
 ]

 [project.urls]
```

Exactly three pieces of movement, and no others:

| Change | Owning phase | Scope |
|---|---|---|
| `version = "0.7.0"` → `"0.7.1"` | Phase 46 plan 46-02 (this milestone's own version bump) | `[project]` version literal |
| `"tox-uv>=1.35,<2"` → `"tox-uv-bare>=1.35,<2"` | Phase 45.2 (QUA-04) | `dev` extra |
| `+ "myst-parser>=5.0"` | Phase 45 (DOC-12) | `docs` extra |

Both moved lines are inside `[project.optional-dependencies]`'s `dev` / `docs` extras — never inside
the runtime `dependencies` array. This is exactly why D-08 scopes the CHANGELOG's `### Verified`
claim to **runtime** dependencies: an unscoped "zero new dependencies" claim would be false to
anyone who diffs the `dev`/`docs` extras or `uv.lock`, but the runtime-scoped claim holds exactly as
measured.

### Verdict — Invariant 1

**PROVEN.** The runtime `[project] dependencies` array is byte-identical between `v0.7.0` and HEAD.
The only dependency-adjacent movement anywhere in `pyproject.toml` is the version literal plus the
two `dev`/`docs`-extra changes named above, both already-shipped by prior phases (45 and 45.2) and
both outside the runtime dependency set.

---

## Invariant 2 — the `@preview` count is still four, no new lockstep site

### The mechanical identity check

```
$ uv run pytest tests/test_preview_version_sync.py -v
tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 33%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 66%]
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED [100%]
============================== 3 passed in 0.04s ===============================

$ uv run pytest tests/test_preview_version_sync.py -q --junit-xml=<scratch>/46-05-preview.xml
tests/test_preview_version_sync.py ...                                   [100%]
============================== 3 passed in 0.04s ===============================

$ grep -o 'failures="[0-9]*"' <scratch>/46-05-preview.xml
failures="0"
$ grep -o 'errors="[0-9]*"' <scratch>/46-05-preview.xml
errors="0"
$ grep -o 'tests="[0-9]*"' <scratch>/46-05-preview.xml
tests="3"
```

All three assertions pass; `failures="0"` and `errors="0"` in the JUnit report, over 3 collected
tests. This mechanically confirms the three code-level declaration sites
(`typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ`) agree on all
four package versions, that each site declares all four expected packages, and that no bundled
`examples/**/*.typ` template pins a stale version.

### Repo-wide `@preview/` enumeration

```
$ grep -rln '@preview/' --include='*.typ' --include='*.py' . | grep -v '^\./\.git\|^\./\.tox\|^\./\.venv'
examples/charged-ieee/approach1/conf.py
examples/charged-ieee/approach2/conf.py
examples/advanced/conf.py
examples/advanced/_templates/custom.typ
tests/test_preview_version_sync.py
examples/charged-ieee/approach2/source/_templates/_template.typ
tests/test_package_template_routing.py
tests/test_template_mitex.py
tests/test_template_engine.py
tests/test_entry_metadata_route_uniformity.py
tests/test_entry_metadata_precedence.py
tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ
tests/test_examples_charged_ieee_gate.py
tests/test_params_exclusivity_gate.py
tests/test_template_codly.py
tests/test_template_assets.py
tests/test_config_other_options.py
tests/fixtures/typst_lang_gate/custom_template_lang/_templates/custom.typ
tests/test_readme_version_sync.py
tests/test_package_only_config_gate.py
tests/fixtures/params_exclusivity_gate/package_params/conf.py
tests/fixtures/admonition_greyscale_probe/_templates/minimal.typ
tests/test_docs_contract_claims_gate.py
tests/fixtures/typst_lang_gate/package_no_lang/conf.py
tests/fixtures/package_only_config_gate/conf.py
tests/fixtures/typst_lang_gate/srcdir_shadow_lang/base.typ
docs/source/_typst/custom_template.typ
typsphinx/writer.py
typsphinx/templates/base.typ
typsphinx/template_engine.py
```

**Per-file classification** (content inspected, not the bare filename), against the surface
`tests/test_preview_version_sync.py`'s own docstring documents (three identity-locked declaration
sites, plus `examples/**/*.typ` as a fourth, drift-only surface):

| Group | Files | Classification |
|---|---|---|
| The three identity-locked declaration sites | `typsphinx/writer.py`, `typsphinx/template_engine.py`, `typsphinx/templates/base.typ` | **Expected** — exactly the surface `test_preview_version_sync.py`'s identity check covers; proven byte-identical above. |
| `examples/**/*.typ` | `examples/advanced/_templates/custom.typ`, `examples/charged-ieee/approach2/source/_templates/_template.typ` | **Expected** — the documented fourth, drift-guarded surface; `test_example_templates_match_canonical_versions` passed above. |
| Fixture-mirror `.typ` files under `tests/fixtures/` | `tests/fixtures/desc_rubric_decoupling_render_gate/golden.typ`, `tests/fixtures/typst_lang_gate/custom_template_lang/_templates/custom.typ`, `tests/fixtures/typst_lang_gate/srcdir_shadow_lang/base.typ`, `tests/fixtures/admonition_greyscale_probe/_templates/minimal.typ` | **Not new / not a hazard** — each carries real `#import "@preview/...:<ver>"` statements, but every one pins exactly the current canonical versions (`codly:1.3.0`, `codly-languages:0.1.10`, `mitex:0.2.7`, `gentle-clues:1.3.1`), verified by direct `grep`. Same precedent as Phase 41's own `41-SC4-INVARIANTS.md` "fixture-mirror" classification — a test fixture re-declaring the canonical import block is expected, not a fifth site. |
| Test `.py` modules asserting emitted-string content | `tests/test_preview_version_sync.py`, `tests/test_package_template_routing.py`, `tests/test_template_mitex.py`, `tests/test_template_engine.py`, `tests/test_entry_metadata_route_uniformity.py`, `tests/test_entry_metadata_precedence.py`, `tests/test_examples_charged_ieee_gate.py`, `tests/test_params_exclusivity_gate.py`, `tests/test_template_codly.py`, `tests/test_template_assets.py`, `tests/test_config_other_options.py`, `tests/test_readme_version_sync.py`, `tests/test_package_only_config_gate.py`, `tests/test_docs_contract_claims_gate.py` | **Not a lockstep hazard** — every occurrence is either a docstring/comment explaining the sync test's own regex, an `assert`/`.count()` check against strings the production code emits, or a `typst_package` test value using an unrelated package (`charged-ieee`, `diagraph`, `tablex`, `my-template`) as fixture data. None of these files are themselves a *declaration site* the extension reads at import-generation time — they test what the three real sites emit. Same "merely reference `@preview/` syntax in fixtures/docstrings" classification `46-RESEARCH.md`'s own verified session recorded. |
| Fixture `conf.py` files | `examples/charged-ieee/approach1/conf.py`, `examples/charged-ieee/approach2/conf.py`, `examples/advanced/conf.py`, `tests/fixtures/params_exclusivity_gate/package_params/conf.py`, `tests/fixtures/typst_lang_gate/package_no_lang/conf.py`, `tests/fixtures/package_only_config_gate/conf.py` | **Not a lockstep hazard** — either set `typst_package` to the unrelated `charged-ieee` package (a different, non-bundled Typst Universe package, not one of the four sync-guarded ones), or (in `examples/advanced/conf.py`) are Python `#`-comments illustrating `typst_package_imports`'s format, never executed as real imports. |
| The already-known, already-deferred fourth site | `docs/source/_typst/custom_template.typ` | **Expected, not new.** Flagged by the v0.6.4-era 30.1 review as an unguarded fourth `@preview` lockstep site, carried in `STATE.md`'s Deferred Items ever since — out of this phase's scope by design. |

**No file under `typsphinx/` or `examples/` appears in this enumeration outside the documented
surface.** Every file outside the three code sites and `examples/**/*.typ` is either a
non-hazard test-assertion/comment file or the single already-known `docs/` site.

### Confirming PR #131 introduced no fifth surface

```
$ grep -n '@preview' typsphinx/builder.py
(no output)

$ git diff v0.7.0..HEAD --name-only -- typsphinx/builder.py
typsphinx/builder.py
```

`typsphinx/builder.py` changed this milestone (via PR #131's `_track_image()` rehoming logic, D-20's
merge) but contains zero `@preview` references — confirmed directly. `_track_image()` is
image-copy bookkeeping, not template or import code, exactly as D-21's read-first note anticipated.
No fifth lockstep surface was introduced.

### Verdict — Invariant 2

**PROVEN.** The `@preview` package count is still four; `test_preview_version_sync.py`'s three
assertions pass with zero failures/errors; the repo-wide enumeration contains no file outside the
documented three-site-plus-`examples/**/*.typ` surface, except the single already-known, already-
deferred `docs/source/_typst/custom_template.typ`; and PR #131's `typsphinx/builder.py` changes
introduce no new `@preview` reference.

---

## Invariant 3 — the prep-only fence over Phase 46

### The plan's literal command, run as written, and why it is non-empty

```
$ git diff origin/main..HEAD --name-only -- typsphinx/
typsphinx/__init__.py
typsphinx/builder.py
typsphinx/template_engine.py
typsphinx/translator.py
typsphinx/writer.py
```

**This is NOT empty, and the reason is a reference-point mismatch, not a fence breach.** This
project's `branching_strategy` is `milestone` (`.planning/config.json`): the entire v0.7.1 milestone
lives on one branch (`gsd/v0.7.1-bug-fix-round`) and is merged to `main` only once, at
`/gsd-complete-milestone`. `origin/main` therefore still sits at `9b2b76b` (the `v0.7.0` release plus
the unrelated, independently-merged PR #131) and contains **none** of Phases 43, 44, 44.1, 44.2, 45,
or 45.1's `typsphinx/` work — all of which legitimately, intentionally modified `typsphinx/` (TBL-04,
TBL-05, FIG-01, CONF-08, BLD-01, TOC-01, CONF-09, CONF-10, CONF-11, CONF-12). `git diff
origin/main..HEAD -- typsphinx/` therefore necessarily surfaces the **whole milestone's** `typsphinx/`
diff, not Phase 46's own contribution — it cannot be empty by construction, regardless of whether
Phase 46 itself is prep-only. Confirmed non-empty for exactly this reason, not because Phase 46 edited
`typsphinx/`.

**[Rule 1 — plan verification-command bug] documented deviation.** The plan's own text states the
purpose plainly: *"this phase changed no `typsphinx/` file"* (singular "this phase" = Phase 46). The
literal command given cannot measure that claim under a milestone-branch strategy — it measures the
whole milestone against `main`, not Phase 46 against the milestone branch's own pre-Phase-46 tip. This
is a bug in the verification command's chosen git reference, not in any source file. Per the executor's
Rule 1 (auto-fix bugs; "wrong queries" is explicitly listed), the correct reference point for "did
Phase 46 itself edit `typsphinx/`" is derived below and used as this invariant's actual verdict basis;
the literal plan command's output is kept above, unedited, for transparency.

### The corrected reference point: Phase 46's own pre-execution tip

```
$ git log fa3bdc3 -1 --format="%H %s"
fa3bdc386ff3378a43a49b27bc0bcc98c8f89297 docs(46): create phase plan
```

`fa3bdc3` is the milestone branch's tip immediately before plan 46-01's first execution commit — it
already contains every prior phase's (43 through 45.2) `typsphinx/` work, and predates any Phase 46
code activity. It is one of the two parents of plan 46-01's merge commit:

```
$ git log c72be91 -1 --format="%H %s" --parents
c72be91 fa3bdc3 9b2b76b merge(46-01): merge origin/main (PR #131) and repair Windows claim-page keys
```

(first parent `fa3bdc3` = the milestone branch's own pre-merge tip; second parent `9b2b76b` =
`origin/main`, i.e. D-20's merge target.)

```
$ git diff fa3bdc3..HEAD --name-only -- typsphinx/
typsphinx/builder.py
```

One file: `typsphinx/builder.py` — brought in by D-20's merge of `origin/main` (PR #131), not authored
by any Phase 46 plan. Confirmed by isolating exactly the merge's own contribution vs. everything
after it:

```
$ git log fa3bdc3..HEAD --oneline -- typsphinx/builder.py
c72be91 merge(46-01): merge origin/main (PR #131) and repair Windows claim-page keys
fe284a7 Update typsphinx/builder.py
fa1ab88 fix: rehome absolute image URIs from Sphinx's ImageConverter/ImageDownloader
```

`fe284a7` and `fa1ab88` are PR #131's own upstream commits (external authorship, already reviewed and
merged to `main` before this phase touched anything), pulled in as merge parents of `c72be91`. This is
exactly D-20's decided, disclosed action ("`origin/main` is merged into the milestone branch at the
head of Phase 46") — not a Phase 46 edit.

### Isolating everything Phase 46 did AFTER the D-20 merge

```
$ git diff c72be91..HEAD --name-only -- typsphinx/
(no output, exit 0)
```

**Empty.** Every commit in Phase 46 after the D-20 merge — all of plans 46-01 (post-merge), 46-02
(version bump), 46-03 (CHANGELOG), and this plan's own Task 1 so far — touched zero files under
`typsphinx/`. 18 commits landed in this range:

```
$ git log c72be91..HEAD --oneline | wc -l
18
```

None of the 18 touch `typsphinx/`, confirmed by the empty diff above.

### Verdict — Invariant 3

**PROVEN, via the corrected reference point.** Phase 46 itself — every commit from its own first
execution task through the D-20 merge and beyond — introduced zero edits under `typsphinx/`. The one
`typsphinx/` file (`builder.py`) that differs between the milestone branch's pre-Phase-46 tip
(`fa3bdc3`) and HEAD arrived exclusively via D-20's deliberate, disclosed merge of already-external,
already-reviewed `origin/main` commits (PR #131) — not via any Phase 46-authored change. This
satisfies the fence's actual intent ("this phase changed no `typsphinx/` file") even though the plan's
literal `origin/main..HEAD` command cannot express that intent correctly under this project's
milestone-branch strategy. Both `_track_image()` defects filed against PR #131
(`rehomed-converted-image-collides-with-srcdir-images-dir`,
`track-image-rehome-escapes-outdir-for-non-doctreedir-abs-uri`) ship unfixed in v0.7.1, per D-27 —
confirmed by the same empty post-merge diff: no Phase 46 commit touches `builder.py` to fix them.

```
$ git tag -l v0.7.1
(no output)
```

No irreversible action was taken while gathering this evidence.

---

## Roll-up verdict

| Invariant | Status | Evidence |
|---|---|---|
| 1 — zero new runtime dependencies | **PROVEN** | `[project] dependencies` byte-identical `v0.7.0` → HEAD; only `dev`/`docs`-extra and version-literal movement elsewhere in `pyproject.toml`, both pre-dating this plan. |
| 2 — `@preview` count still four, no new lockstep site | **PROVEN** | `test_preview_version_sync.py` 3/3 passed, `failures="0"`/`errors="0"`; repo-wide enumeration contains no file outside the documented sync surface except the already-known `docs/source/_typst/custom_template.typ`; PR #131's `builder.py` introduces no `@preview` reference. |
| 3 — the prep-only fence over Phase 46 | **PROVEN** (via corrected reference point; plan's literal `origin/main..HEAD` command is non-empty for a documented, explained reason — a milestone-branch reference-point mismatch, not a fence breach) | `git diff c72be91..HEAD -- typsphinx/` (post-D-20-merge tip to current HEAD) is empty; the only pre-existing `typsphinx/` movement (`builder.py`) is D-20's disclosed merge of external PR #131, not Phase 46's own authorship. |

**All three milestone invariants hold.** No irreversible action was taken: `git tag -l v0.7.1` is
empty throughout. One deviation is recorded and fully explained ([Rule 1] Invariant 3's plan-literal
command), with both the literal command's output and the corrected measurement shown side by side for
transparency, per this plan's own "figures must come from a command in the file" requirement.

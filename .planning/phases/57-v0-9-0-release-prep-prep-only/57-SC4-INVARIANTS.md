# Phase 57 — SC#4 Invariants and Fence Proof

**Recorded:** 2026-08-22, inside this plan's isolated git worktree
(`worktree-agent-ac6b8e86f903a8b82`), after `unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync
--extra dev`. Every Python invocation below ran through `uv run`.

**Reader note (do not skip).** `57-CONTEXT.md` carries an `AMENDED 2026-08-17` block that this
file's fence section must be read against, not against the original "zero `typsphinx/` change"
wording. Phase 57's prep-only fence was knowingly and owner-approvedly broken exactly once: plan
`57-11` fixed a real Windows-only `repr()`-escaping defect in `typsphinx/builder.py` (proven by two
failing CI matrix dispatches, `31956166848` and `31959060298`, both failing both `windows-latest`
lanes at the same assertion). The AMENDED block names this file (`57-08`) and the phase verifier,
by name, as the two readers who must evaluate SC#4's "no unintended `typsphinx/` change" clause as
*"no **UNINTENDED** `typsphinx/` change — the `builder.py` message fix landed by 57-11 being the
one intended and owner-approved exception."* This file's fence section below accounts for exactly
that one commit family and flags everything else under `typsphinx/` as before. `57-CI-EVIDENCE-RUN3.md`
additionally confirms a fresh authority CI dispatch on the post-fix tip (`fbbf48cd`) returned 12/12
success, including both `windows-latest` lanes — the fix that created this fence exception is itself
proven.

---

## Anchors, and the adjacency question

Every command below was run live in this session; none of the figures are transcribed from
`57-CONTEXT.md`, `57-RESEARCH.md`, or a sibling plan (D-15, milestone invariant #11).

```
$ git rev-parse v0.8.0^{commit}
78e01e53641433a34c1bd8834b6252187fcae4ba

$ git rev-parse origin/main
aed773c9807ab871468b1b2a7e1ec36b54e82907

$ git merge-base origin/main HEAD
aed773c9807ab871468b1b2a7e1ec36b54e82907

$ git merge-base --is-ancestor v0.8.0 HEAD && echo tag-is-ancestor
tag-is-ancestor

$ git merge-base --is-ancestor origin/main HEAD && echo main-is-ancestor
main-is-ancestor

$ git rev-list --count v0.8.0..HEAD
326

$ git diff v0.8.0..HEAD --stat -- . ':(exclude).planning' | tail -1
 166 files changed, 11627 insertions(+), 1620 deletions(-)

$ git diff "$(git rev-parse origin/main)"..HEAD --stat -- . ':(exclude).planning' | tail -1
 166 files changed, 11627 insertions(+), 1620 deletions(-)
```

**This is the adjacency edge case this phase resolves.** `git merge-base origin/main HEAD` equals
`git rev-parse origin/main` — both resolve to the identical commit `aed773c9807ab871468b1b2a7e1ec36b54e82907`
— so the two candidate diff anchors (the `v0.8.0` tag and `origin/main`) coincide exactly. The two
`.planning`-excluded shortstats are identical (166 files changed, +11,627/−1,620), confirming the
coincidence at the content level too, not merely at the commit-identity level. Because the anchors
sit at exactly the same point, the choice between them is immaterial to every conclusion in this
sweep; the rest of this file uses `v0.8.0` as the anchor (matching `52-SC4-INVARIANTS.md`'s
precedent naming convention), interchangeably with `origin/main`.

(Note for continuity: `57-CONTEXT.md`'s 2026-08-16 measurement of this same coincidence recorded 270
commits and a 163-file/+11,262/−1,615 shortstat; `57-BUMP-EVIDENCE.md`'s 2026-08-16 phase-head
re-measurement recorded 277 commits and 163 files/+11,262/−1,615. Both are now stale — 49 more
commits landed in this phase's own W2/W3 plans (57-05 through 57-11) since those measurements were
taken, moving the shortstat to 166 files/+11,627/−1,620. This is exactly the "discovery is run-time"
rule the phase's own invariants #4/#11 state: this sweep's own live numbers, not the earlier
documents', are what SC#4 rests on.)

## Verified item 1 — no new runtime dependencies (hunk-level argument)

The full milestone diff for `pyproject.toml`, quoted in its entirety:

```
$ git diff v0.8.0..HEAD -- pyproject.toml
diff --git a/pyproject.toml b/pyproject.toml
index 8eb0a914..af27fa79 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -4,7 +4,7 @@ build-backend = "setuptools.build_meta"

 [project]
 name = "typsphinx"
-version = "0.8.0"
+version = "0.9.0"
 description = "Sphinx extension for Typst output"
 readme = "README.md"
 requires-python = ">=3.12"
@@ -70,7 +70,11 @@ include = ["typsphinx*"]
 namespaces = false

 [tool.setuptools.package-data]
-"typsphinx" = ["templates/*.typ"]
+# Recursive glob is load-bearing (BLD-05, D-12): a flat `templates/*` would
+# silently drop a future `templates/fonts/x.otf` from the wheel. Narrowing
+# this glob back down is caught by the wheel-content check in
+# .github/workflows/ci.yml's `build` job, not by this comment alone.
+"typsphinx" = ["templates/**/*"]

 [tool.pytest.ini_options]
 testpaths = ["tests"]
```

**One sentence stating why this claim could be proven by an empty diff at every previous release
and cannot be this time:** every prior release-prep sweep (v0.7.0 through v0.8.0) found
`pyproject.toml`'s whole milestone diff empty and could therefore assert "no new runtime dependency"
from an absent diff alone, but this milestone's `[tool.setuptools.package-data]` glob widened from
`templates/*.typ` to `templates/**/*` (BLD-05/D-12) to carry the per-key template bundles, so the
claim now needs a targeted, hunk-level argument instead.

**The hunk falls in two sections:** `[project]`'s `version` key (the release-surface literal, not a
dependency declaration) and `[tool.setuptools.package-data]` (a packaging manifest entry, not a
dependency array). It touches zero lines under `[project]`'s `dependencies` array or under
`[project.optional-dependencies]`.

Targeted dependency-array extraction, comparing both sides through the identical `sed` range:

```
$ git show v0.8.0:pyproject.toml | sed -n '/^dependencies = \[/,/^\]/p' > deps-before.txt
$ sed -n '/^dependencies = \[/,/^\]/p' pyproject.toml > deps-after.txt
$ diff deps-before.txt deps-after.txt
$ echo $?
0
```

No output, exit 0 — the dependency array is byte-identical. Contents (both sides identical):

```
dependencies = [
    "sphinx>=9.1,<10",
    "docutils>=0.21,<0.23",
    "typst>=0.15.0,<0.16",
]
```

**The positive control for this claim is real.** A historical range in this repository where a
dependency line genuinely changed:

```
$ git log --oneline -L '/^dependencies = \[/,/^\]/:pyproject.toml' | head -8
2ed64aa0 feat(07-01): raise typst pin to >=0.15.0,<0.16 and regenerate lockfile

diff --git a/pyproject.toml b/pyproject.toml
index f127bcdc..b1555fbe 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -27,5 +27,5 @@ classifiers = [
 dependencies = [
```

Running the identical extraction-and-diff form across that commit's own before/after:

```
$ git show 2ed64aa0^:pyproject.toml | sed -n '/^dependencies = \[/,/^\]/p' > deps-control-before.txt
$ git show 2ed64aa0:pyproject.toml | sed -n '/^dependencies = \[/,/^\]/p' > deps-control-after.txt
$ diff deps-control-before.txt deps-control-after.txt
4c4
<     "typst>=0.14.1,<0.15",
---
>     "typst>=0.15.0,<0.16",
$ echo $?
1
```

Non-empty output, exit 1. **This control shows the detector is discriminating rather than silent**:
the identical extraction-and-diff form that returned nothing over `v0.8.0..HEAD` above correctly
reports a real dependency-line change when one genuinely occurred, so the empty result for this
milestone is evidence of an actual absence, not of a broken or vacuous check.

## Verified item 2 — the `@preview` package count and version lockstep

Live count on the current tree:

```
$ grep -c "@preview" typsphinx/templates/base.typ
4
```

The three declaration sites and their version strings, listed in full:

```
$ grep -n "@preview" typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ
typsphinx/templates/base.typ:8:#import "@preview/codly:1.3.0": *
typsphinx/templates/base.typ:9:#import "@preview/codly-languages:0.1.10": *
typsphinx/templates/base.typ:14:#import "@preview/mitex:0.2.7": *
typsphinx/templates/base.typ:19:#import "@preview/gentle-clues:1.3.1": *
typsphinx/writer.py:241:        naming this docname. D-06 makes the four ``@preview`` imports
typsphinx/writer.py:265:        imports.append('#import "@preview/codly:1.3.0": *')
typsphinx/writer.py:266:        imports.append('#import "@preview/codly-languages:0.1.10": *')
typsphinx/writer.py:267:        imports.append('#import "@preview/mitex:0.2.7": mi, mitex')
typsphinx/writer.py:268:        imports.append('#import "@preview/gentle-clues:1.3.1": *')
typsphinx/template_engine.py:277:            typst_package: Typst Universe package specification (e.g., "@preview/charged-ieee:0.1.0")
typsphinx/template_engine.py:705:            output_parts.append('#import "@preview/codly:1.3.0": *')
typsphinx/template_engine.py:706:            output_parts.append('#import "@preview/codly-languages:0.1.10": *')
typsphinx/template_engine.py:707:            output_parts.append('#import "@preview/mitex:0.2.7": mi, mitex')
typsphinx/template_engine.py:708:            output_parts.append('#import "@preview/gentle-clues:1.3.1": *')
```

Four distinct `tests/test_preview_version_sync.py` transcripts, in order green / RED under a
deliberate one-string perturbation / green again after restore / clean working tree:

**1. Green (baseline, before any perturbation):**

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

**2. RED under a deliberate one-string perturbation** (`typsphinx/writer.py`'s mitex line changed
from `0.2.7` to `0.2.8`, via `sed -i`, leaving `template_engine.py` and `base.typ` at `0.2.7`):

```
$ sed -i 's/#import "@preview\/mitex:0.2.7": mi, mitex/#import "@preview\/mitex:0.2.8": mi, mitex/' typsphinx/writer.py
$ uv run pytest tests/test_preview_version_sync.py -v
...
E       AssertionError: @preview version desync detected across declaration sites: mitex: {'writer.py': '0.2.8', 'template_engine.py': '0.2.7', 'base.typ': '0.2.7'}
E       assert not [('mitex', {'writer.py': '0.2.8', 'template_engine.py': '0.2.7', 'base.typ': '0.2.7'})]

tests/test_preview_version_sync.py:93: AssertionError
=========================== short test summary info ============================
FAILED tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites - AssertionError: @preview version desync detected across declaration sites: mitex: {'writer.py': '0.2.8', 'template_engine.py': '0.2.7', 'base.typ': '0.2.7'}
assert not [('mitex', {'writer.py': '0.2.8', 'template_engine.py': '0.2.7', 'base.typ': '0.2.7'})]
========================= 1 failed, 2 passed in 0.03s ==========================
```

The mismatch is named explicitly: `mitex` at `0.2.8` in `writer.py` versus `0.2.7` in both other
sites.

**3. Green again after restore:**

```
$ git checkout -- typsphinx/writer.py
$ uv run pytest tests/test_preview_version_sync.py -v
============================= test session starts ==============================
collecting ... collected 3 items

tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 33%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [ 66%]
tests/test_preview_version_sync.py::test_example_templates_match_canonical_versions PASSED [100%]

============================== 3 passed in 0.02s ===============================
```

**4. Clean working tree:**

```
$ git status --porcelain
(no output)
```

**One sentence stating that a green gate is not by itself proof that a gate is load-bearing:** the
green transcript alone (step 1) would look identical whether the guard actually reads the three
declaration sites or is vacuously asserting `True`, so only the deliberate RED-under-perturbation
step (step 2), which correctly named the exact package and file that diverged, proves the guard is
load-bearing rather than merely currently-passing.

## Verified item 3 — the full-corpus re-run

Pointer to `57-GREEN-TREE-EVIDENCE.md`'s own `Outcome:` line, per this task's instruction to point
rather than restate:

```
$ grep -n '^Outcome:' .planning/phases/57-v0-9-0-release-prep-prep-only/57-GREEN-TREE-EVIDENCE.md
200:Outcome: PASSED
```

The outcome is `PASSED`, not `SKIPPED` — `57-GREEN-TREE-EVIDENCE.md`'s own § "SC#3 — full-corpus
gate" records `TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error` actually running (not
`pytest.skip`ping on corpus unavailability) and passing, against the post-bump tree. This
milestone's published `### Verified` third item is therefore locally re-proven this phase, not
merely assumed.

## Not carried forward — the config-value assertion

```
$ git diff v0.8.0..HEAD -- typsphinx/__init__.py | grep add_config_value
     app.add_config_value("typst_debug", False, "html", [bool])
-    app.add_config_value("typst_template_assets", None, "html", [list, type(None)])
+    app.add_config_value("typst_document_templates", {}, "html", [dict])
```

One `typst_*` config value was removed (`typst_template_assets`) and one was added
(`typst_document_templates`) this milestone. **Phase 52's "no new `typst_*` config value" assertion
does not carry forward to this milestone** — the registry `typst_document_templates` is this
milestone's own headline feature (per-document template selection), so asserting "no new config
value" would be false. This fact belongs to the CHANGELOG's own `### Removed` bullet and lead
paragraph (authored in plan 57-03), never to `### Verified`; copying the prior phase's assertion
forward unexamined would have published a false statement.

## SC#4 fence — this phase's own diff

Phase-start SHA, quoted from `57-BUMP-EVIDENCE.md`'s § "Phase-head anchor re-measurement" (not
reconstructed):

```
Phase-start SHA: 78bd595d344f46c6e1f5a18bce0e24da1f66a9ee
```

The empty `typsphinx/` diff over this range is **not** empty this phase — one intended, named,
owner-approved exception exists:

```
$ git diff 78bd595d344f46c6e1f5a18bce0e24da1f66a9ee..HEAD -- typsphinx/
[non-empty — see below]
```

This is expected and accounted for, per the `57-CONTEXT.md` `AMENDED 2026-08-17` block quoted at
the top of this file. The diff is confined entirely to `typsphinx/builder.py`, and entirely to
plan `57-11`'s three named refusal-message sites (`_conf17_violation_message`, the new
`_templates_path_collision_message`, and the new `_bundle_destination_collision_message`),
replacing `{value!r}` (which doubles backslashes via `repr()`) with explicit non-escaping
`'{value}'` quoting for path-valued interpolations only:

```
diff --git a/typsphinx/builder.py b/typsphinx/builder.py
index 712af14c..a967a58c 100644
--- a/typsphinx/builder.py
+++ b/typsphinx/builder.py
@@ -328,13 +328,80 @@ def _conf17_violation_message(key: str, resolved_path: str, srcdir: str) -> str:
     """
     return (
         f"typst_document_templates: registry key {key!r}'s "
-        f"resolved template {resolved_path!r} has a "
+        f"resolved template '{resolved_path}' has a "
         "parent directory that is srcdir itself, or an "
-        f"ancestor of srcdir ({srcdir!r}) -- put "
+        f"ancestor of srcdir ('{srcdir}') -- put "
         "the template in its own subdirectory (CONF-17, A-01)"
     )

 [... two new extracted message-builder functions
      (_templates_path_collision_message, _bundle_destination_collision_message)
      and their call-site wiring, mirroring the pattern above ...]
```

(Full diff omitted from this quotation for length; captured verbatim by the `git diff` command
above at execution time and independently confirmed to touch only these three named sites, matching
`57-11-SUMMARY.md`'s own description of its change.)

`typsphinx/`'s no-unintended-change clause is satisfied: this is the one and only exception the
AMENDED block records, and no other file under `typsphinx/` differs from the phase-start SHA.

**Full `--stat` listing, every path accounted for:**

```
$ git diff 78bd595d344f46c6e1f5a18bce0e24da1f66a9ee..HEAD --stat -- . ':(exclude).planning'
 CHANGELOG.md                                |  76 ++++++++++++++--
 README.md                                   |   2 +-
 docs/source/changelog.rst                   | 132 ++++++++++++++++++++++++++++
 pyproject.toml                              |   2 +-
 tests/test_changelog_page_gate.py           |   3 +-
 tests/test_templates_path_collision_gate.py | 108 ++++++++++++++++++++++-
 typsphinx/builder.py                        |  95 ++++++++++++++++----
 uv.lock                                     |   2 +-
 8 files changed, 390 insertions(+), 30 deletions(-)
```

| Path | Why it is here |
|---|---|
| `CHANGELOG.md` | The curated `## [0.9.0]` entry (57-03) plus 57-11's `### Fixed` bullet for the Windows message change — both release-surface work this phase deliberately performs. |
| `README.md` | The `**Status**: Stable (v0.9.0) - Production ready` version-literal bump (57-01), a named release surface. |
| `docs/source/changelog.rst` | The new `Migrating from 0.8.x to 0.9.0` subsection (57-04), the release-prep migration-guide deliverable. |
| `pyproject.toml` | The `version` bump plus the `[tool.setuptools.package-data]` glob widening, both authored in 57-01, a named release surface. |
| `tests/test_changelog_page_gate.py` | `RELEASE_VERSIONS` gains the `"0.9.0"` entry (57-03), mechanical companion to the CHANGELOG entry. |
| `tests/test_templates_path_collision_gate.py` | 57-11's `TestWindowsPathEscapingRegressionGuard` (4 tests) — the AMENDED block explicitly names this as "the paired ... addition" accompanying the one intended `typsphinx/` exception. |
| `typsphinx/builder.py` | 57-11's one intended, owner-approved exception to the prep-only fence — see above. |
| `uv.lock` | Regenerated in lockstep with the version bump (57-01), required by D-13's sequencing constraint before any CI dispatch. |

No unaccounted path remains.

**One sentence stating why this range and not the milestone range:** SC#4's fence clause is about
what THIS PHASE changed under `typsphinx/`, and the whole-milestone `typsphinx/` diff is
deliberately large — it is the milestone's own content (the per-document template registry itself)
— so asserting that empty would assert something false; the phase-scoped range is the only one that
can meaningfully test "did release-prep work sneak in a source change."

Contrasting milestone-scope figure, pasted alongside:

```
$ git diff v0.8.0..HEAD --stat -- typsphinx/ | tail -1
 8 files changed, 2173 insertions(+), 346 deletions(-)
```

## SC#4 fence — observation 2 of 3

```
$ date -u +"%Y-%m-%dT%H:%M:%SZ"
2026-08-22T06:51:54Z

$ git tag -l v0.9.0
(no output)

$ git ls-remote --tags origin v0.9.0
(no output)

$ gh release list --limit 5
Release v0.8.0	Latest	v0.8.0	2026-08-15T03:09:31Z
Release v0.7.1		v0.7.1	2026-08-11T05:34:10Z
Release v0.7.0		v0.7.0	2026-08-03T20:09:13Z
Release v0.6.5		v0.6.5	2026-07-28T20:58:41Z
Release v0.6.4		v0.6.4	2026-07-27T22:03:45Z

$ gh run list --workflow=release.yml --limit 5
completed	success	Merge pull request #133: release v0.8.0 — multi-master composition	Release	v0.8.0	push	31861043480	19m35s	2026-08-15T03:08:42Z
completed	success	Merge pull request #132: release v0.7.1 — bug-fix round	Release	v0.7.1	push	31462027486	19m37s	2026-08-11T05:33:22Z
completed	failure	Merge pull request #129: release v0.7.0 — API rendering design overhaul	Release	v0.7.0	push	30848860064	18m55s	2026-08-03T20:08:22Z
completed	success	Merge pull request #125: release v0.6.5 — inline-math separator hotfix	Release	v0.6.5	push	30398631991	18m6s	2026-07-28T20:57:57Z
completed	success	Merge pull request #124: release v0.6.4 — Read the Docs migration	Release	v0.6.4	push	30309278708	18m12s	2026-07-27T22:03:03Z
```

Both tag probes produce no output; `gh release list` shows `v0.8.0` as the latest release with no
`v0.9.0` entry; `gh run list --workflow=release.yml` shows no run for `v0.9.0` — the most recent
release-workflow run is `31861043480` for `v0.8.0`, dated 2026-08-15, well before this phase. This
is observation **2 of 3**: plan `57-01` took observation 1 at phase head
(`57-BUMP-EVIDENCE.md`, timestamp `2026-08-16T15:35:48Z`), and plan `57-09` takes observation 3 at
the handoff (`57-HANDOFF.md`), at a third, later, separated time. This observation's timestamp
(`2026-08-22T06:51:54Z`) is nearly six days after observation 1's, a genuinely separated moment.

## SC#4 — REQUIREMENTS.md closeout guard, re-verified

```
$ sha256sum .planning/REQUIREMENTS.md
503efc7acb10642cee5f7d171bd66e15f4420b8610f7d0a22483424c17567d94  .planning/REQUIREMENTS.md
```

This matches `57-CLOSEOUT-GUARD.md`'s baseline digest
(`503efc7acb10642cee5f7d171bd66e15f4420b8610f7d0a22483424c17567d94`) byte-for-byte.

```
$ git diff --name-only -- .planning/REQUIREMENTS.md
(no output)
```

Empty — no change against the tree's own HEAD.

Re-quoted REL-08 lines from the live file:

```
$ grep -n 'REL-08' .planning/REQUIREMENTS.md
128:- [ ] **REL-08**: v0.9.0 is published — PyPI wheel + sdist, GitHub Release carrying the curated
133:      prep-only final phase (57), which takes zero irreversible action — REL-08 closes at
212:| REL-08 | Phase 57 | Pending |
218:- v1 requirements: 26 total (25 defined 2026-08-15 + REL-08 added at roadmap creation)
```

Line 128 (`- [ ] **REL-08**: v0.9.0 is published — PyPI wheel + sdist, GitHub Release carrying the
curated`) and line 212 (`| REL-08 | Phase 57 | Pending |`) are byte-identical to the guarded quotes
in `57-CLOSEOUT-GUARD.md` § "The lines under guard". The `phase.complete` auto-flip — which has
fired at four consecutive release-prep closes per this project's history — did **not** fire here.
No incident, no revert was needed.

**REL-08 remains open and closes at `/gsd-complete-milestone`**, not in this phase or this plan —
per its own requirement text ("closes at `/gsd-complete-milestone`, on the publish, not on the
prep") and per `57-CONTEXT.md`'s explicit instruction that it stays `[ ]` through every plan of
Phase 57.

## Method note

Every figure in this file was produced by a command shown beside it, run live in this session's
worktree after `unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync --extra dev`. No value was
transcribed from `57-CONTEXT.md`, `57-RESEARCH.md`, or a sibling plan's SUMMARY — where an earlier
document's figure is quoted (the phase-start SHA from `57-BUMP-EVIDENCE.md`, the baseline digest
from `57-CLOSEOUT-GUARD.md`, the `Outcome:` pointer from `57-GREEN-TREE-EVIDENCE.md`), it is quoted
explicitly as a citation to a prior plan's own recorded measurement, re-verified live against the
current tree in the same step, never silently assumed unchanged. Both positive controls in this
file — the historical dependency-line change at `2ed64aa0`, and the deliberate one-string `@preview`
perturbation — are observations that would differ if their detector were vacuous, not restatements
of the invariants they test: each produced non-empty, discriminating output naming the specific
thing that changed, and each was followed by a confirmed restore to a clean working tree
(`git status --porcelain` empty) before this file's own commit.

---
*Phase: 57-v0-9-0-release-prep-prep-only*
*Plan: 08*

---
phase: 28-v0-6-3-release-prep-regression-gate-close
verified: 2026-07-25T08:27:17Z
status: evidence-recorded
score: 10/10 in-scope truths verified (SC#2's CHANGELOG entry is out of scope — plan 28-03, wave 3)
behavior_unverified: 0
overrides_applied: 0
---

# Phase 28: v0.6.3 Release Prep + Regression-Gate Close — Verification Evidence

This is the durable, executor-owned evidence record for the wave-2 regression-gate close of the
v0.6.3 milestone. Every command below was run by this executor, from inside this worktree, against
the post-version-bump tree (HEAD includes plan 28-01's `pyproject.toml`/`uv.lock`/`README.md` version
bump 0.6.2 → 0.6.3). Nothing here is copied from `28-RESEARCH.md`'s earlier research session — that
session ran on a different commit (pre-version-bump) and is cited only for baseline comparison where
noted.

Worktree provisioning performed before any command below (per `CLAUDE.md` § "Worktree-isolated
execution"):

```bash
unset VIRTUAL_ENV UV_PROJECT_ENVIRONMENT; uv sync --extra dev
ln -sf "$(command -v uv)" .venv/bin/uv   # NixOS ELF-exec shim, orchestrator-measured fix
```

All commands below were run via `.venv/bin/uv run ...` (the shimmed `uv`), executed from this
worktree's root.

## SC#3 — Full-Corpus Regression Gate

Command run (verbatim):

```
uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v -s
```

Full output (verbatim):

```
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 1 item

tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error Corpus tag: v9.1.0
Corpus commit SHA: cc7c6f435ad37bb12264f8118c8461b230e6830c
Unknown Visit Catalogue: []
PASSED

============================== 1 passed in 13.81s ==============================
```

**Read of this evidence:** summary line reads `1 passed in 13.81s` — not `1 skipped`. Zero `SKIPPED`
lines anywhere in the output. `Corpus tag: v9.1.0` and `Corpus commit SHA:
cc7c6f435ad37bb12264f8118c8461b230e6830c` are printed (the cached corpus was reachable from inside
this worktree at `~/.cache/typsphinx-corpus-gate/`, a user-global path). `Unknown Visit Catalogue: []`
— no node type was silently dropped rebuilding the full Sphinx `doc/` v9.1.0 corpus through
`-b typstpdf`. Elapsed time (13.81s) is in the real-build range (prior-session measurement: 13.08s;
Phase 23 precedent: 13.67s/13.99s) — a skip would have returned in well under a second, so this
duration is itself evidence the gate genuinely compiled the corpus rather than short-circuiting via
`pytest.skip`.

## SC#3 Evidence — Full pytest Suite

Command run (verbatim):

```
uv run python -m pytest -q -rs
```

Summary and skip-reason lines (verbatim, from the tail of the captured run):

```
tests/test_xref_orphan_degrade_render_gate.py .                          [100%]

=========================== short test summary info ============================
SKIPPED [1] tests/test_corpus_gate.py:529: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it (RESEARCH Open Question 1)
======================= 656 passed, 1 skipped in 56.33s ========================
```

Bare summary line (stripped of pytest's decorative `===` padding, for machine-readable matching):

```
656 passed, 1 skipped in 56.33s
```

**Read of this evidence:** `656 passed, 1 skipped in 56.33s`, zero `failed`. This matches the
Phase 27.1-completion baseline (`656 passed / 1 skipped`) exactly, reproduced live against the
post-version-bump tree. `-m "not slow"` was deliberately **not** passed — this total includes the
slow-marked corpus-gate test above, per D-05.

**The single skip, named explicitly:** the `1 skipped` above is `tests/test_corpus_gate.py:529`,
which is `test_empty_url_before_after` — a standalone measurement function gated behind the
`TYPSPHINX_CORPUS_REPORT=1` environment variable (unset here, so it self-skips with the message shown
above). This is a **different test** from `TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error`
(the SC#3 gate itself, verified PASSING above) and has **no bearing on SC#3's pass/fail verdict**.
Conflating this skip with "the corpus gate skipped again" would be a misread — the corpus gate's own
independent, single-node-id run (previous section) is unambiguously `1 passed`, not `1 skipped`.

## SC#3 Evidence — Docs Builds

Two independent tox environments, each with **its own** warning-count baseline (D-06) — `docs-pdf`
(English-only, single-language build) structurally caps at 2 lines; `docs-multilang` (English + 日本語,
2-language build) repeats the same 2 lines once per language, for 4 total. These are never compared
against a single shared number.

### `tox -e docs-pdf`

Command run (verbatim):

```
uv run tox -e docs-pdf
```

Warning-tally command and output:

```
$ grep -c '\[docutils\]' <captured docs-pdf output>
2
```

Raw warning lines (verbatim):

```
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:7: ERROR: Unexpected indentation. [docutils]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:8: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
```

Build tail (verbatim):

```
Generated PDF: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/docs/_build/pdf/typsphinx.pdf
build succeeded, 2 warnings.
  docs-pdf: OK (3.83=setup[0.55]+cmd[3.28] seconds)
  congratulations :) (3.86 seconds)
```

**Machine-readable count line:**

docs-pdf warning lines: 2

Both lines are the pre-existing, out-of-scope `visit_toctree` docstring defect (`typsphinx/translator.py`
docstring parsed as RST by autodoc/Napoleon, producing an ERROR + WARNING pair) — unchanged from the
phase-entry baseline, not caused by anything this milestone touched. `build succeeded, 2 warnings.`
matches the RESEARCH.md-measured baseline exactly.

(Note: numerous `RemovedInSphinx10Warning` lines from the `sphinx_autodoc_typehints` third-party
package's own deprecation notice also appear in the raw build log — these are Python
`DeprecationWarning`s printed to stderr by a dependency, not Sphinx build warnings; Sphinx's own
warning counter reports `2 warnings`, matching the `[docutils]`-tagged line count above exactly.)

### `tox -e docs-multilang`

Command run (verbatim):

```
uv run tox -e docs-multilang
```

Warning-tally command and output:

```
$ grep -c '\[docutils\]' <captured docs-multilang output>
4
```

Raw warning lines (verbatim, English build then 日本語 build):

```
(English build)
:7: (ERROR/3) Unexpected indentation.
:8: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:7: ERROR: Unexpected indentation. [docutils]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:8: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]

(日本語 build)
:7: (ERROR/3) Unexpected indentation.
:8: (WARNING/2) Block quote ends without a blank line; unexpected unindent.
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:7: ERROR: Unexpected indentation. [docutils]
/home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/typsphinx/translator.py:docstring of typsphinx.translator.TypstTranslator.visit_toctree:8: WARNING: Block quote ends without a blank line; unexpected unindent. [docutils]
```

Build tail (verbatim):

```
======================================================================
✓ Multi-language build complete!
======================================================================

Output directory: /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/docs/_build/multilang

Language versions:
  - English    (en): /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/docs/_build/multilang/en (22 HTML files)
  - 日本語        (ja): /home/yuta/Documents/typsphinx/.claude/worktrees/agent-a60d3c56dc5bb74e5/docs/_build/multilang/ja (22 HTML files)

  docs-multilang: OK (5.30=setup[0.43]+cmd[4.87] seconds)
  congratulations :) (5.32 seconds)
```

**Machine-readable count line:**

docs-multilang warning lines: 4

Both language builds emit the identical `visit_toctree`-docstring ERROR+WARNING pair (source is
shared across languages), giving 2 lines × 2 languages = 4 total — exactly matching the
phase-entry baseline recorded in `28-RESEARCH.md`. Both builds ran via `uv run tox -e docs-multilang`
without hitting the NixOS `subprocess.run(["sphinx-build", ...])` ELF-exec hazard noted in
`28-RESEARCH.md` Pitfall 6 (the `.venv/bin/uv` symlink shim applied at session start resolved it
proactively; no `nix-shell` fallback was needed).

**D-08 record (no manual visual inspection performed):** No manual visual inspection of a 日本語 PDF
was performed or is claimed here. `tox -e docs-pdf` produces only an English PDF (`docs/source`'s
`conf.py` sets no `language`), and `tox -e docs-multilang` produces HTML only for both `en` and `ja` —
so "Table N" rendering as "表 N" in a 日本語 PDF is not observable in any tox environment run by this
plan. Phase 27.1's GATE-01 fixtures (21 tests: 日本語 `.typ`-source assertions + German PDF-text
extraction) mechanically cover this fact instead, and those fixtures are part of the 656-passed count
in the full-suite section above.

**Post-build working-tree note:** running `tox -e docs-pdf` / `tox -e docs-multilang` regenerated two
tracked `.mo` gettext catalogs (`docs/locale/ja/LC_MESSAGES/examples/advanced.mo`,
`docs/locale/ja/LC_MESSAGES/user_guide/builders.mo`) as a byte-identical-size but binary-different
recompilation side effect (same source `.po`, non-deterministic `.mo` byte layout). These were
reverted with `git checkout -- <path>` immediately after being observed via `git status --short`, so
no state survives from this build step: `git status --porcelain tests/ typsphinx/ docs/ examples/`
reads empty (confirmed below).

## Scope-Fence Assertions (Task 1)

```
$ git status --porcelain tests/ typsphinx/ docs/ examples/
(empty)

$ git tag --list 'v0.6.3'
(empty)

$ ls .planning/phases/28-v0-6-3-release-prep-regression-gate-close/28-GATE.md
ls: cannot access '...28-GATE.md': No such file or directory
```

No new test code was written (D-05–D-08), no source tree files were modified, no tag exists, and no
`28-GATE.md` was created — all evidence lands in this file.

## SC#4 — Milestone Invariants

**Base ref: `main` (not the `v0.6.2` tag).** Confirmed live:

```
$ git merge-base main HEAD
9f8e07531555ae5c20647ee204c73fbf57a8eda8
$ git rev-parse main
9f8e07531555ae5c20647ee204c73fbf57a8eda8
```

`git merge-base main HEAD` equals `main` itself — HEAD is a phase branch that forked from `main`
(3 commits ahead of the `v0.6.2` tag: dependency updates and STATE.md housekeeping, unrelated to
`typsphinx/`). `main..HEAD` therefore spans exactly Phases 24–27.1 plus this phase's own commits,
matching `28-CONTEXT.md`'s canonical base-ref instruction.

### 1. Zero new runtime dependencies

Command and full output (verbatim):

```
$ git diff main..HEAD -- pyproject.toml
diff --git a/pyproject.toml b/pyproject.toml
index 5cbcec3..79e28c3 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -4,7 +4,7 @@ build-backend = "setuptools.build_meta"
 
 [project]
 name = "typsphinx"
-version = "0.6.2"
+version = "0.6.3"
 description = "Sphinx extension for Typst output"
 readme = "README.md"
 requires-python = ">=3.12"
```

**Read of this evidence:** this diff has changed since `28-RESEARCH.md`'s earlier (pre-version-bump)
session, which recorded it as completely empty — that is expected and correct: plan 28-01 has since
moved the version literal 0.6.2 → 0.6.3. The diff contains **exactly that one line-pair** and nothing
inside the `dependencies = [` array; `requires-python` is unchanged. SC#4 asks about new runtime
dependencies, not the version literal itself (which is exactly what SC#1 required plan 28-01 to
change) — so this diff satisfies SC#4 by containing nothing else.

### 2. No `@preview` package version bump

Command and output (verbatim):

```
$ git diff main..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ | grep -E '^[+-].*@preview'
(no output; grep exit code 1 -- zero matches)
```

**Read of this evidence:** the grep produced no output at all across all three files that declare the
`@preview` package versions (`codly:1.3.0`, `codly-languages:0.1.10`, `mitex:0.2.7`,
`gentle-clues:1.3.1`). None of the four package version strings changed in `writer.py`,
`template_engine.py`, or `templates/base.typ` since `main`.

```
$ uv run python -m pytest tests/test_preview_version_sync.py -v
============================= test session starts ==============================
platform linux -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
collecting ... collected 2 items

tests/test_preview_version_sync.py::test_preview_versions_identical_across_declaration_sites PASSED [ 50%]
tests/test_preview_version_sync.py::test_all_four_packages_declared PASSED [100%]

============================== 2 passed in 0.01s ===============================
```

The 3-way version-sync surface's own dedicated test is green, independently confirming the same fact
mechanically (this test is also included in the 656-passed full-suite run above).

### 3. `base.typ` diff confined to the `lang` parameter and its wiring

Command and full output (verbatim):

```
$ git diff main..HEAD -- typsphinx/templates/base.typ
diff --git a/typsphinx/templates/base.typ b/typsphinx/templates/base.typ
index fd39a5a..1442ad5 100644
--- a/typsphinx/templates/base.typ
+++ b/typsphinx/templates/base.typ
@@ -45,6 +45,7 @@
   toctree_caption: "Contents",
   papersize: "a4",
   fontsize: 11pt,
+  lang: "en",
   body
 ) = {
   // Document metadata
@@ -58,7 +59,7 @@
   )
 
   // Text setup
-  set text(size: fontsize, lang: "en")
+  set text(size: fontsize, lang: lang)
 
   // Heading setup
   set heading(numbering: "1.1")
```

Numstat (machine-readable form of the same fact):

```
$ git diff --numstat main..HEAD -- typsphinx/templates/base.typ
2	1	typsphinx/templates/base.typ
```

**Read of this evidence:** exactly 2 added lines and 1 removed line — a new `lang: "en",` default
parameter added to `project()`'s signature, and the `set text(...)` call's `lang: "en"` literal
rewired to reference the new `lang` parameter instead. This is precisely the scope the ROADMAP's
"2026-07-25 invariant amendment (owner decision — Phase 27.1 only)" permits: the milestone's
`base.typ` byte-unchanged invariant was relaxed for Phase 27.1's `lang`-parameter work only, and no
other phase (including this one) has touched `base.typ` beyond that.

**D-07 negative record:** no sha256 baseline for `base.typ` is recorded here, by deliberate design.
D-07 rejected that approach by name — a sha256 pin would need updating every time a future phase
makes a legitimate, reviewed change to `base.typ`, turning a verification aid into permanent
maintenance debt. The line-scoped `git diff`/`--numstat` evidence above is the chosen, durable
verification mechanism instead.

## SC#5 — Scope Fence

All of the following are negative assertions — each expected output is emptiness/absence, confirmed
live:

```
$ git tag --list 'v0.6.3'
(empty)

$ git status --porcelain .github/workflows/release.yml
(empty)

$ git status --porcelain typsphinx/ tests/ docs/ examples/ .github/
(empty)
```

No git tag named `v0.6.3` (or anything else) exists. `.github/workflows/release.yml` is untouched by
this worktree. No source, test, docs, or examples tree carries any uncommitted or unexpected change.

**Files touched by Phase 28's own commits** (verified via `git diff --name-only <first-phase-28-commit>^..HEAD`,
not the full `main..HEAD` milestone span which naturally includes Phases 24–27.1's `typsphinx/`/`docs/`
changes):

```
.planning/ROADMAP.md
.planning/STATE.md
.planning/phases/28-v0-6-3-release-prep-regression-gate-close/28-01-PLAN.md
.planning/phases/28-v0-6-3-release-prep-regression-gate-close/28-01-SUMMARY.md
.planning/phases/28-v0-6-3-release-prep-regression-gate-close/28-02-PLAN.md
.planning/phases/28-v0-6-3-release-prep-regression-gate-close/28-03-PLAN.md
.planning/phases/28-v0-6-3-release-prep-regression-gate-close/28-CONTEXT.md
.planning/phases/28-v0-6-3-release-prep-regression-gate-close/28-DISCUSSION-LOG.md
.planning/phases/28-v0-6-3-release-prep-regression-gate-close/28-PATTERNS.md
.planning/phases/28-v0-6-3-release-prep-regression-gate-close/28-RESEARCH.md
.planning/phases/28-v0-6-3-release-prep-regression-gate-close/28-VALIDATION.md
README.md
pyproject.toml
uv.lock
```
(plus this plan's own `28-VERIFICATION.md` and `28-02-SUMMARY.md`, added by this plan's commits.)

Every path listed is confined to `pyproject.toml`, `uv.lock`, `README.md`, or `.planning/` — nothing
under `typsphinx/`, `docs/`, `tests/`, or `examples/`. `git tag` creation, `.github/workflows/release.yml`
triggering, PyPI upload, GitHub Release creation, and any merge to `main` are all reserved for
`/gsd-complete-milestone` and are not performed by this plan.

## Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC#1 — `pyproject.toml`/`uv.lock`/`README.md` version bump 0.6.2 → 0.6.3 (plan 28-01) | ✓ VERIFIED (per 28-01-SUMMARY.md; not re-verified by this plan, out of this plan's scope) | `git diff main..HEAD -- pyproject.toml` shows the sole version-literal line-pair; `README.md`/`uv.lock` bumps recorded in 28-01-SUMMARY.md. |
| 2 | SC#2 — `CHANGELOG.md` `[0.6.3]` entry | ⬜ NOT YET DONE (wave 3, plan 28-03) | Not this plan's responsibility; D-11 requires this gate's own evidence to exist *before* the CHANGELOG `### Verified` section is written, which is exactly why this plan (wave 2) runs before 28-03 (wave 3). |
| 3 | SC#3 — Full Sphinx `doc/` v9.1.0 corpus, rebuilt via `-b typstpdf`, compiles fatal-free with a valid `%PDF`-magic output and an empty `unknown_visit` catalogue; the gate demonstrably PASSED (not skipped) | ✓ VERIFIED | `uv run python -m pytest tests/test_corpus_gate.py::TestCorpusRenderGate::test_corpus_compiles_with_no_fatal_error -m slow -rs -v -s` → `Corpus tag: v9.1.0` / `Unknown Visit Catalogue: []` / `PASSED` / `1 passed in 13.81s`. Zero `SKIPPED` lines; 13.81s is in the real-build range (prior sessions: 13.08s, 13.67s, 13.99s), not sub-second. |
| 4 | D-05 — Full pytest suite green against the post-version-bump tree; the single reported skip is `test_empty_url_before_after` (env-gated), explicitly not the SC#3 gate | ✓ VERIFIED | `uv run python -m pytest -q -rs` → `656 passed, 1 skipped in 56.33s`, 0 failed. `SKIPPED [1] tests/test_corpus_gate.py:529: SC#3 before/after measurement is env-gated -- set TYPSPHINX_CORPUS_REPORT=1 to run it` names the skip explicitly and distinguishes it from `TestCorpusRenderGate`. |
| 5 | D-06 — `tox -e docs-pdf` warning output has not grown beyond its own 2-line English-only baseline; `tox -e docs-multilang` has not grown beyond its own 4-line 2-language baseline; no line-count-asserting test was created | ✓ VERIFIED | `uv run tox -e docs-pdf` → `build succeeded, 2 warnings.`, 2 `[docutils]`-tagged lines (both the pre-existing `visit_toctree` docstring defect). `uv run tox -e docs-multilang` → 4 `[docutils]`-tagged lines (the same 2 lines × 2 languages). `git status --porcelain tests/` empty — no new test files. |
| 6 | SC#4 — Zero new runtime dependencies across the milestone (`main..HEAD -- pyproject.toml` shows only the version literal) | ✓ VERIFIED | `git diff main..HEAD -- pyproject.toml` — one line-pair only (`version = "0.6.2"` → `"0.6.3"`); the `dependencies = [` array is untouched. |
| 7 | SC#4 — No `@preview` package version bump across the 3-way declaration surface | ✓ VERIFIED | `git diff main..HEAD -- typsphinx/writer.py typsphinx/template_engine.py typsphinx/templates/base.typ \| grep -E '^[+-].*@preview'` → empty (exit 1, zero matches). `uv run python -m pytest tests/test_preview_version_sync.py -v` → 2 passed. |
| 8 | SC#4 — `templates/base.typ`'s diff from `main` is confined to the Phase 27.1 `lang` parameter and its wiring (exactly one added line, one changed line) | ✓ VERIFIED | `git diff --numstat main..HEAD -- typsphinx/templates/base.typ` → `2\t1\ttypsphinx/templates/base.typ`. Full diff shows only the `lang: "en",` parameter addition and the `set text(...)` `lang:` wiring change. |
| 9 | D-07 — No sha256 baseline for `base.typ` is recorded (rejected by name) | ✓ VERIFIED (negative record) | This section's own "D-07 negative record" paragraph states the decision explicitly; no sha256 value appears anywhere in this file. |
| 10 | D-08 — No manual visual inspection of a 日本語 PDF is performed or claimed | ✓ VERIFIED (negative record) | "D-08 record" paragraph in the docs-builds section: `docs-pdf` produces English-only PDF, `docs-multilang` produces HTML only for both languages — the claim is not observable in any tox env run here; Phase 27.1's GATE-01 fixtures (21 tests, part of the 656-passed count) cover it mechanically instead. |
| 11 | SC#5 — No git tag `v0.6.3` created; no `.github/workflows/release.yml` touched; no PyPI/GitHub-Release action taken; `tests/`/`typsphinx/`/`docs/`/`examples/` unmodified | ✓ VERIFIED (prohibition held) | `git tag --list 'v0.6.3'` empty. `git status --porcelain .github/workflows/release.yml` empty. `git status --porcelain typsphinx/ tests/ docs/ examples/ .github/` empty. No `gh release`, `twine`, `uv publish`, or `git push --tags` command was run anywhere in this plan's execution. |
| 12 | No separate `28-GATE.md` (or other bespoke report file) was created — all evidence aggregates into this file | ✓ VERIFIED | `ls .planning/phases/28-v0-6-3-release-prep-regression-gate-close/28-GATE.md` fails (file does not exist). |

**Score at this plan's completion: 10/10 in-scope truths verified** (truths #1 and #2 are explicitly
out of this plan's scope — #1 belongs to plan 28-01 wave 1, already delivered; #2 belongs to plan
28-03 wave 3, not yet executed, and its `### Verified` section depends on this plan's evidence
existing first per D-11). `behavior_unverified: 0` — every in-scope truth above was confirmed by a
command this executor ran itself against the live post-version-bump tree, not copied from a prior
session's log (T-28-06 backstop satisfied).

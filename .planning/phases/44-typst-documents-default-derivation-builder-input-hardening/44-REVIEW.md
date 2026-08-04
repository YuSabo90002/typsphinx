---
phase: 44-typst-documents-default-derivation-builder-input-hardening
reviewed: 2026-08-04T06:11:48Z
depth: standard
files_reviewed: 16
files_reviewed_list:
  - typsphinx/builder.py
  - typsphinx/__init__.py
  - tests/test_builder.py
  - tests/test_builder_requirement13.py
  - tests/test_default_typst_documents_derivation.py
  - tests/test_default_typst_documents_gate.py
  - tests/test_empty_typst_documents_optout_gate.py
  - tests/test_non_str_docname_gate.py
  - tests/fixtures/default_typst_documents_gate/conf.py
  - tests/fixtures/default_typst_documents_gate/index.rst
  - tests/fixtures/empty_typst_documents_optout_gate/conf.py
  - tests/fixtures/empty_typst_documents_optout_gate/index.rst
  - tests/fixtures/explicit_typst_documents_wins_gate/conf.py
  - tests/fixtures/explicit_typst_documents_wins_gate/index.rst
  - tests/fixtures/non_str_docname_gate/conf.py
  - tests/fixtures/non_str_docname_gate/index.rst
findings:
  critical: 1
  warning: 1
  info: 1
  total: 3
status: issues_found
---

# Phase 44: Code Review Report

**Reviewed:** 2026-08-04T06:11:48Z
**Depth:** standard
**Files Reviewed:** 16
**Status:** issues_found

## Summary

Reviewed the `typst_documents` default-derivation function (`_default_typst_documents`),
its registration in `__init__.py`, the `isinstance(docname, str)` hardening added to
`TypstPDFBuilder.finish()`, and every new/updated test and fixture for this phase.

The derivation function itself is verified sound against every focus area named in the
review brief: it is a pure function of its `config` argument (no memoization, no
instance state — confirmed against Sphinx's `Config.__getattr__`, which literally
re-invokes a callable default on every unset access and never caches it), and it never
produces a path separator, traversal sequence, or absolute path for any `project` value
— `make_filename_from_project`'s own `[^a-zA-Z0-9_-]` stripping regex (Sphinx-owned, not
typsphinx-owned) guarantees that, degrading to the literal string `"sphinx"` for
empty/punctuation-only/non-ASCII-only project names. The `isinstance` guard in `finish()`
is placed before every use of `docname` that would otherwise raise, and its message leaks
nothing but a `repr()` of the offending config value. Explicit-vs-derived precedence
(`SC#2`) is correctly gate-tested against real `sphinx-build` subprocesses, not just
against the derivation function in isolation, and the eight-row degradation-table test is
a genuine purity gate (it would only pass across all eight rows if the function reads
`config` fresh on every call).

However, **the derivation introduces a reachable, reproducible data-loss / build-failure
bug** (CR-01 below) because neither `_default_typst_documents` nor the pre-existing
`_resolve_output_stem`/`write()` path it feeds ever checks the derived (or an explicit)
target-name stem for collision against another real docname's own output path, or against
the reserved `_template.typ` infrastructure file. Before this phase, triggering that
collision required an explicit, deliberately-crafted `typst_documents` entry; after this
phase, it is reachable with **zero configuration** — an ordinary `project` name whose
slugified form happens to match an existing document's docname (e.g. `project = "Chapter
1"` alongside a `chapter1.rst`, a very ordinary docs layout) silently corrupts the `-b
typst` output and hard-fails the `-b typstpdf` build. Both were reproduced live against
this checkout (details in CR-01). No test in this phase's fixture set exercises this
collision scenario.

## Critical Issues

### CR-01: Derived (and explicit) `typst_documents` target names are never checked for collision with a real docname's own output path or with the reserved `_template.typ`, causing silent content loss or a hard build failure

**File:** `typsphinx/builder.py:28-47` (`_default_typst_documents`), interacting with
`typsphinx/builder.py:156-261` (`_resolve_output_stem`), `typsphinx/builder.py:357-417`
(`write()`), and `typsphinx/builder.py:544-615` (`_write_template_file()`)

**Issue:**

`_default_typst_documents` derives a single master target name purely from
`make_filename_from_project(config.project)`, with no awareness of the other docnames in
the project or of the `_template.typ` file `_write_template_file()` writes,
unconditionally, at the outdir root before any document is written. `_resolve_output_stem`
(which resolves both the derived entry and any explicit `typst_documents` entry) likewise
performs no collision check against `self.env.found_docs` or against `"_template"`. Since
`write()` writes every docname in `sorted()` order into a path keyed only by the resolved
stem, whichever docname is processed **last** silently overwrites whatever an earlier
docname (or the pre-written template file) wrote to the same path — with no warning, no
error, and (for `-b typst`) exit code 0.

Reproduced live (both cases run against this exact worktree, not hypothetical):

**Case 1 — collision with a real docname.** `project = "Chapter 1"`, with `index.rst`
(the root doc, toctree-including `chapter1.rst`) and `chapter1.rst` (a completely ordinary
docs layout: a project named after its first chapter). `make_filename_from_project("Chapter
1")` → `"chapter1"`, so the derived entry names the **index** master's output
`chapter1.typ` — identical to the real `chapter1.rst` document's own (unrenamed) output
path.

- `sphinx-build -b typst`: exits 0. Only one file, `chapter1.typ`, ends up on disk — it is
  the **index** master's content (which itself does `include("chapter1.typ")`, now
  self-referential). The real "Chapter One" document (`CHAPTERBODY` sentinel) is
  permanently gone from the build output with zero warning.
- `sphinx-build -b typstpdf`: exits 2. `typst.compile()` raises `TypstError: cyclic
  import` at `chapter1.typ`, surfaced through the phase's own aggregate `ExtensionError`
  path — at least loud, but a build that was never misconfigured by the user now fails
  outright, purely because of an incidental name coincidence with zero explicit
  `typst_documents` setting.

**Case 2 — collision with the reserved `_template.typ`.** `project = "_Template"` (a
plausible internal/staging project name — underscore is one of the characters
`make_filename_from_project`'s regex explicitly preserves). `make_filename_from_project
("_Template")` → `"_template"`, so the derived master target is `_template.typ`, which
`_write_template_file()` already wrote (correctly) before `write()` runs. The master
document write then overwrites the **shared template file itself** with the master's own
body. Reproduced: `sphinx-build -b typstpdf` exits 2 with the same `TypstError: cyclic
import`, now located at `_template.typ` — meaning every document that does `#import
"_template.typ": project` (i.e. every master in the build) would break, not just the one
colliding entry.

Neither case is exercised by any of this phase's new gate tests
(`test_default_typst_documents_gate.py`, `test_empty_typst_documents_optout_gate.py`,
`test_non_str_docname_gate.py`), all of which use fixture `project` values deliberately
chosen so the derived stem never collides with an existing docname or `_template`.

**Fix:** Add a collision check in `_resolve_output_stem` (or immediately after it, in
`write_doc`/`finish`) that rejects — with a `logger.warning` and a safe fallback to the
docname itself, matching the existing D-06/D-07 degenerate-target handling style — any
resolved stem that equals another docname actually present in `self.env.found_docs` (other
than the docname currently being resolved) or that equals the reserved `"_template"`
basename. Sketch:

```python
# After the existing path-guard block, before returning `stem`:
if stem != docname and (stem in self.env.found_docs or stem == "_template"):
    logger.warning(
        "typst_documents target name %r for docname %r collides with an "
        "existing document or the reserved template file -- falling back "
        "to %r" % (stem, docname, docname)
    )
    return docname
```

This should be covered by a new gate test mirroring the `Chapter 1`/`chapter1.rst` and
`_Template` repros above (both derived-default-triggered and explicit-`typst_documents`-
triggered variants), asserting no file is silently overwritten and a warning fires.

## Warnings

### WR-01: The corrected D-03 "empty list" warning wording asserts a fact that does not hold for every value that reaches its branch

**File:** `typsphinx/builder.py:927-941`

**Issue:** `typst_documents = getattr(self.config, "typst_documents", [])` (line 927, no
`or []` normalization, unlike the equivalent lookups in `_compute_master_included_docnames`
line 140 and `_resolve_output_stem` line 183) is followed by `if not typst_documents:` at
line 929, which is also true for `typst_documents = None` — a plausible user mistake given
`typst_documents` is documented and type-declared as `[list]`, but Sphinx's
`check_confval_types` only warns (does not coerce or reject) a `None` value. The new
message text asserts unconditionally:

```python
logger.warning(
    "typst_documents is explicitly set to an empty list -- "
    "nothing will be compiled. Remove the setting entirely to "
    "use the derived default (root_doc/project/author)."
)
```

For `typst_documents = None` this message is factually wrong (it was not set to an empty
list) even though the behavior it warns about is otherwise correct.

**Fix:** Guard against non-list falsy values explicitly, or soften the wording so it does
not assert a specific literal value:

```python
if not typst_documents:
    logger.warning(
        "typst_documents resolved to nothing to compile (empty or unset "
        "to a falsy value) -- remove the setting entirely to use the "
        "derived default (root_doc/project/author), or set it to a "
        "non-empty list."
    )
    return
```

## Info

### IN-01: Vacuous assertion in `test_default_typst_documents_gate.py` cannot distinguish pass from fail

**File:** `tests/test_default_typst_documents_gate.py:120-123`

**Issue:** `assert "Nothing to compile" not in result.stderr` appears to intend to check
that the *old* pre-phase-44 warning ("No documents defined in typst_documents. Nothing to
compile.") does not fire. But the current code's only related warning text (D-03, in
`TypstPDFBuilder.finish()`) reads "...nothing will be compiled..." (lowercase "nothing",
different surrounding words) — the exact substring `"Nothing to compile"` can never appear
in stderr regardless of whether the underlying bug this assertion is meant to catch exists,
making the assertion permanently vacuous (would pass identically against a broken future
regression that reintroduces some other wrongly-worded warning).

**Fix:** Either drop the assertion (the preceding `pdf_file.exists()` checks already prove
the derived default was consulted) or replace it with a positive assertion tied to current
wording, e.g. `assert "explicitly set to an empty list" not in result.stderr`.

---

_Reviewed: 2026-08-04T06:11:48Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

---

## Orchestrator independent re-measurement of CR-01

The reviewer's CR-01 is a BLOCKER, so the execute-phase orchestrator reproduced it
independently rather than accepting the agent's report. All commands below were run by the
orchestrator on the main checkout at `3b45fa6`, using `uv run python -m sphinx`.

**Fixture** (`project = "Chapter 1"`, no `typst_documents` line, `index.rst` toctree-including
`chapter1.rst`; the chapter body carries the literal marker `UNIQUE-CHAPTER-MARKER-XYZ`):

### A. Post-change tree, zero configuration — CONFIRMED silent loss

```
$ uv run python -m sphinx -b typst src out
writing output... [chapter1] done
writing output... [index] done
build succeeded.

$ ls out/*.typ
out/_template.typ
out/chapter1.typ          <- index.rst's own output; chapter1.rst's output is GONE

$ grep -c 'UNIQUE-CHAPTER-MARKER-XYZ' out/chapter1.typ
0
```

`build succeeded`, exit 0, no warning. `chapter1.rst`'s rendered body is not on disk anywhere.

### B. Pre-phase-equivalent configuration — NO collision

Re-run of the same source with `typst_documents = []` appended to `conf.py`, which reproduces
exactly the config state that existed before this phase (the old `[]` default):

```
$ ls out2/*.typ
out2/_template.typ
out2/chapter1.typ
out2/index.typ            <- both documents present

$ grep -c 'UNIQUE-CHAPTER-MARKER-XYZ' out2/chapter1.typ
1
```

**This establishes the regression boundary precisely.** The collision *mechanism* in
`_resolve_output_stem` is pre-existing and was already reachable by an explicit
`typst_documents` target name. What this phase changes is that it is now reachable with
**zero configuration** — on the very path CONF-08 exists to make work.

### C. `-b typstpdf` on the same project — hard failure

```
sphinx.errors.ExtensionError: typstpdf: 1 master document(s) failed:
  index: Typst compilation failed: TypstError: cyclic import
  Location: out3/chapter1.typ
  Details: cyclic import
```

### D. `project = "_Template"` — the shared template file is clobbered

```
$ ls -l out4/*.typ
460  out4/_template.typ        <- was 2438 bytes of template infrastructure

$ grep -c '^#let project' out4/_template.typ
0
```

`_write_template_file()` writes `_template.typ` first; the master's own write then overwrites
it, so the `#let project(...)` definition every emitted document imports no longer exists.

**Verdict: CR-01 CONFIRMED as reported.** All four measurements reproduce. The reviewer's
statement that no gate test in this phase covers the scenario is also confirmed — every new
fixture's `project` value is collision-free by construction.

---
phase: 44-typst-documents-default-derivation-builder-input-hardening
reviewed: 2026-08-04T00:00:00Z
depth: standard
files_reviewed: 28
files_reviewed_list:
  - typsphinx/builder.py
  - typsphinx/__init__.py
  - tests/test_builder.py
  - tests/test_builder_output_stem.py
  - tests/test_builder_requirement13.py
  - tests/test_default_typst_documents_derivation.py
  - tests/test_default_typst_documents_gate.py
  - tests/test_empty_typst_documents_optout_gate.py
  - tests/test_non_str_docname_gate.py
  - tests/test_typst_documents_collision_gate.py
  - tests/fixtures/default_typst_documents_gate/conf.py
  - tests/fixtures/default_typst_documents_gate/index.rst
  - tests/fixtures/empty_typst_documents_optout_gate/conf.py
  - tests/fixtures/empty_typst_documents_optout_gate/index.rst
  - tests/fixtures/explicit_typst_documents_wins_gate/conf.py
  - tests/fixtures/explicit_typst_documents_wins_gate/index.rst
  - tests/fixtures/non_str_docname_gate/conf.py
  - tests/fixtures/non_str_docname_gate/index.rst
  - tests/fixtures/derived_docname_collision_gate/conf.py
  - tests/fixtures/derived_docname_collision_gate/index.rst
  - tests/fixtures/derived_docname_collision_gate/chapter1.rst
  - tests/fixtures/derived_template_collision_gate/conf.py
  - tests/fixtures/derived_template_collision_gate/index.rst
  - tests/fixtures/explicit_docname_collision_gate/conf.py
  - tests/fixtures/explicit_docname_collision_gate/index.rst
  - tests/fixtures/explicit_docname_collision_gate/chapter1.rst
  - tests/fixtures/explicit_template_collision_gate/conf.py
  - tests/fixtures/explicit_template_collision_gate/index.rst
findings:
  critical: 1
  warning: 2
  info: 2
  total: 5
status: issues_found
---

# Phase 44: Code Review Report

**Reviewed:** 2026-08-04T00:00:00Z
**Depth:** standard
**Files Reviewed:** 28
**Status:** issues_found

## Summary

Reviewed plan 44-05's CR-01 gap-closure (the collision guard added to
`_resolve_output_stem`) together with the full CONF-08/BLD-01 surface from
plans 01-04 (`_default_typst_documents`, its `__init__.py` registration, the
`isinstance(docname, str)` hardening in `TypstPDFBuilder.finish()`), and
every test/fixture in the file list.

The CR-01 fix itself is sound for the exact two scenarios it targets
(derived-or-explicit target colliding with a real docname's own output
path, and colliding with the reserved `_template.typ`): the four new
subprocess gate tests reproduce the original silent-corruption and
hard-failure repros from the prior review and confirm both are now warned
and safely degraded. `_default_typst_documents` remains a pure function of
its `config` argument, the degradation table matches
`make_filename_from_project` exactly, and explicit-vs-derived precedence
(SC#2) is gate-tested against real `sphinx-build` subprocesses.

However, adversarial testing against the same collision-guard code found a
**new, reproducible silent-data-loss bug the CR-01 guard does not cover**:
two `typst_documents` entries whose *targets* collide with **each other**
(rather than with a real docname or `_template`) are not detected at all —
one master's entire compiled output silently overwrites the other's, with
no warning and exit code 0 for both `-b typst` and `-b typstpdf`. This is
the same failure class Phase 44's own CR-01 was written to close, on the
very function (`_resolve_output_stem`) plan 44-05 just modified, and it is
easier to trigger than either of the two now-fixed cases (an ordinary
two-master project with a copy-pasted or coincidentally-identical target
name, no docname coincidence required). See CR-02 below, with a live
reproduction against this checkout.

WR-01 and IN-01 from the prior (2026-08-04T06:11:48Z) review remain present
and unchanged, and are explicitly out of scope for 44-05 per the phase
owner's decision — re-listed below under their original IDs, not as new
findings.

## Critical Issues

### CR-02: Two `typst_documents` entries whose target names collide with each other (not with a real docname or `_template`) are not detected — one master's output silently overwrites the other's

**File:** `typsphinx/builder.py:264-283` (`_resolve_output_stem`'s CR-01
collision guard), interacting with `typsphinx/builder.py:384-444` (`write()`)
and `typsphinx/builder.py:925-1039` (`TypstPDFBuilder.finish()`)

**Issue:**

The CR-01 guard added by plan 44-05 only rejects a resolved target whose
directory-qualified effective path equals `self.env.found_docs` (a real
document's own output path) or the reserved `"_template"` basename. It
never checks the resolved target against **other entries in the same
`typst_documents` list**. When two masters (whether both explicit, or one
explicit and one derived) resolve to the same effective path, `write()`
writes both docnames' bodies to that one path in `sorted(docnames)` order,
so the alphabetically-later docname's `write_doc()` call silently
overwrites the earlier one's file with no warning and no error — the
earlier master's document vanishes entirely from the build output.

Live reproduction against this checkout (`-b typst`):

```python
# conf.py
typst_documents = [
    ("index", "manual.typ", "Index Master", author),
    ("other", "manual.typ", "Other Master", author),
]
```

```
$ sphinx-build -b typst src build
writing output... [index] done
writing output... [other] done
build succeeded.

$ ls build/*.typ
build/_template.typ
build/manual.typ

$ grep -c 'INDEX-MASTER-BODY-UNIQUE' build/manual.typ
0
$ grep -c 'OTHER-MASTER-BODY-UNIQUE' build/manual.typ
1
```

`build succeeded`, exit 0, **zero warning**. The `index` master's entire
document is gone from disk with no trace.

The `-b typstpdf` counterpart is worse — it does not even fail loudly (the
docname-collision case at least hard-fails with `TypstError: cyclic
import`; this one does not, because there is no self-reference):

```
$ sphinx-build -b typstpdf src build
...
Compiling 2 master document(s) to PDF...
Generated PDF: build/manual.pdf
Generated PDF: build/manual.pdf
build succeeded.

$ ls build/*.pdf
build/manual.pdf
```

Both masters "successfully" compile and both log lines claim
`Generated PDF: build/manual.pdf` — the exact same path, twice — silently
discarding the `index` master's PDF. A user watching the log sees two
successful compiles and one file; nothing before this points at data loss.

This is not a synthetic edge case: it happens whenever any two
`typst_documents` entries share a target name (explicit copy-paste error,
two masters both left at an identical explicit `"manual.typ"`, or one
explicit entry that happens to match what `_default_typst_documents` would
derive for a second, unlisted master added later). None of the four new
CR-01 gate tests, nor any other test in this file list, exercises a
two-entry `typst_documents` with colliding targets.

**Fix:** Extend the CR-01 guard to also check the resolved effective path
against every *other* `typst_documents` entry's resolved effective path
(not just `found_docs`/`_template`), e.g. by resolving all entries' stems
up front (in `prepare_writing()` or lazily with memoization) and tracking
which effective paths have already been claimed by an earlier entry in
list order:

```python
# In prepare_writing(), after self.writer is created:
self._claimed_output_paths: dict[str, str] = {}  # effective path -> docname

# In _resolve_output_stem, after the existing found_docs/_template check
# and before the final `return stem`:
claimed_by = self._claimed_output_paths.get(effective)
if effective != docname and claimed_by is not None and claimed_by != docname:
    logger.warning(
        f"typst_documents target name {target!r} for docname {docname!r} "
        f"collides with the target already claimed by {claimed_by!r} -- "
        f"falling back to {docname!r}"
    )
    return docname
self._claimed_output_paths.setdefault(effective, docname)
```

Add a gate test mirroring `test_typst_documents_collision_gate.py`'s
existing pattern: two masters with identical explicit target names, asserting
both `.typ`/`.pdf` files exist under their own docnames (or one falls back
with a warning) rather than one silently vanishing.

## Warnings

### WR-01 (deferred, unchanged from prior review): The corrected D-03 "empty list" warning wording asserts a fact that does not hold for every value that reaches its branch

**File:** `typsphinx/builder.py:954-968`

Re-verified present and unchanged: `typst_documents = getattr(self.config,
"typst_documents", [])` (no `or []` normalization) followed by
`if not typst_documents:` is also true for `typst_documents = None`, for
which the message "typst_documents is explicitly set to an empty list" is
factually wrong. Per the phase owner's decision recorded in
`44-CONTEXT.md`, this is explicitly out of scope for plan 44-05 and is
re-listed here under its original ID rather than as a new finding. See the
prior review (`2026-08-04T06:11:48Z`, preserved further down in this file's
git history) for the full analysis and suggested fix.

### WR-02: The CR-01 collision warning (and every other `_resolve_output_stem` warning branch) is logged twice under `-b typstpdf`, because `write_doc()` and `finish()` both re-resolve the same docname without caching

**File:** `typsphinx/builder.py:880-924` (`TypstPDFBuilder.write_doc`) and
`typsphinx/builder.py:1001` (`TypstPDFBuilder.finish`)

**Issue:** `TypstPDFBuilder.write_doc()` calls
`self._resolve_output_stem(docname)` once per document during the write
phase; `TypstPDFBuilder.finish()` calls it again, per master, during the
PDF-compile phase, purely to re-derive the `.typ` read-back path. Because
`_resolve_output_stem` is stateless and re-runs its full warning logic on
every call, any docname that triggers a `logger.warning` branch (the
D-06/D-07 path guard, the degenerate-target fallback, or the new CR-01
collision guard) logs that warning **twice** for `-b typstpdf`, while
`-b typst` (whose `write_doc()` never calls `_resolve_output_stem` a second
time) logs it once. Verified live against this checkout:

```
$ sphinx-build -b typstpdf tests/fixtures/derived_docname_collision_gate build
writing output... [index]WARNING: typst_documents target name 'chapter1.typ'
  for docname 'index' collides with an existing document or the reserved
  template file -- falling back to 'index'
...
WARNING: typst_documents target name 'chapter1.typ' for docname 'index'
  collides with an existing document or the reserved template file --
  falling back to 'index'
```

The same collision is reported twice for the same docname, which reads as
if two separate problems were found (or that a compile ran twice) and is
inconsistent with the single-warning behavior of `-b typst` for the exact
same misconfiguration. This duplicate-logging pattern predates Phase 44 for
the pre-existing D-06/D-07 branches, but the new CR-01 collision warning
inherits it unmodified, and none of the new gate tests assert warning
*count* (they only assert substring presence), so the duplication is
undetected by the current suite.

**Fix:** Cache the resolved stem per docname for the duration of a build
(e.g. `self._resolved_stems: dict[str, str] = {}` populated in
`write_doc()` and consulted by `finish()` instead of re-calling
`_resolve_output_stem`), so every warning branch logs exactly once
regardless of builder.

## Info

### IN-01 (deferred, unchanged from prior review): Vacuous assertion in `test_default_typst_documents_gate.py` cannot distinguish pass from fail

**File:** `tests/test_default_typst_documents_gate.py:120-123`

Re-verified present and unchanged: `assert "Nothing to compile" not in
result.stderr` can never fail given the current D-03 wording ("...nothing
will be compiled...", different substring), making the assertion
permanently vacuous. Per the phase owner's decision, explicitly out of
scope for plan 44-05 and re-listed here under its original ID. See the
prior review for the full analysis and suggested fix.

### IN-02: `_resolve_output_stem` and `TypstPDFBuilder.finish()` are both large, multi-branch functions, which makes gaps like CR-02 easy to introduce and easy to miss in review

**File:** `typsphinx/builder.py:156-288` (`_resolve_output_stem`, ~132
lines) and `typsphinx/builder.py:925-1039` (`TypstPDFBuilder.finish`, ~115
lines)

**Issue:** `_resolve_output_stem` now carries five independent concerns in
one function body: entry lookup, suffix stripping, the D-06/D-07 path
guard, the degenerate-target guard, and the CR-01 collision guard — each
individually well-commented and well-tested in isolation, but the
function's overall length and branching depth is exactly the kind of
surface where a sibling collision case (CR-02) is easy to add a guard for
in one spot and miss in another. Similarly, `finish()` interleaves
malformed-entry handling, the BLD-01 type guard, stem re-resolution, and
PDF compilation in one 115-line loop body.

**Fix:** Not a functional defect on its own — flagged as a maintainability
note. Consider extracting the path guard and the collision guard in
`_resolve_output_stem` into two separately-named, separately-tested helper
functions (e.g. `_guard_path_bearing_target(stem) -> str` and
`_guard_collision(docname, stem) -> str | None`), and extracting `finish()`'s
per-entry validation (malformed tuple / non-str docname / stem resolution)
into a helper that returns either a validated `(docname, typ_file)` pair or
a failure message, so future collision classes are checked in one place
that already returns "warn and fall back" rather than being re-derived at
each new guard's insertion point.

---

_Reviewed: 2026-08-04T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_

---

## Appendix A — Archived prior review (2026-08-04T06:11:48Z, plans 01-04)

This review file is rewritten wholesale on each `/gsd-code-review` run. The prior
review's CR-01 finding and the orchestrator's independent re-measurement of it are
cited by `44-GATE-EVIDENCE-05.md` ("44-REVIEW.md § CR-01", "§ Orchestrator independent
re-measurement of CR-01 A-D"), so they are preserved verbatim below rather than left as
dangling references. CR-01 itself is FIXED as of plan 44-05 (commit `edca2de`); the
content below is historical. Original file also recoverable at commit `6aa452b`.

<details>
<summary>Prior review, verbatim</summary>

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

</details>
